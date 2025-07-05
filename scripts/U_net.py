# system
from pathlib import Path
from argparse import ArgumentParser

# data
import pickle
import nrrd

# tensorflow
from tensorflow import keras
from keras.layers import Input, Conv2D, MaxPooling2D, ReLU
from keras.layers import BatchNormalization, Conv2DTranspose, Concatenate, Normalization
from keras.models import Model


parser = ArgumentParser()

parser.add_argument('-t', "--train", 
                    help="Enable training mode",
                    action="store_true")

parser.add_argument('-p', "--predict",
                    help="Predict mode, specify location of pre-trained model.",
                    type=str)

parser.add_argument('-e', "--epochs",
                    help="Set amount of epochs for training",
                    type=int)

parser.add_argument('-a', "--learning_rate",
                    help="Set learning rate",
                    type=float)

parser.add_argument('-b', "--batch_size",
                    help="specify size of batch",
                    type=int)

parser.add_argument('-s', "--model_name",
                    help="Save trained model as [model_name].keras",
                    type=str)

parser.add_argument('-x', "--shape",
                    help="Pass the shape of the data, typical is: 'X;Y;c'",
                    type=str)

parser.add_argument('-d', "--training_data",
                    help="""Path to python pickle file containing dict with following entries:

                        data = {"seg_test": seg_test,
                                "seq_test": seq_test,
                                "seg_train": seg_train,
                                "seq_train": seq_train,
                                "seg_val": seg_val,
                                "seq_val": seq_val}
                    """,
                    type=str)

parser.add_argument('-i', "--input_directory",
                    help="Input directory sequences",
                    type=str)

parser.add_argument('-o', "--output_directory",
                    help="Output directory predictions", 
                    type=str)

def convolutional_operaration(input_tensor, filters=64):
    # Convolutional block one
    conv1 = Conv2D(filters, kernel_size=(3,3), padding="same")(input_tensor)
    batch_norm1 = BatchNormalization()(conv1)
    activation1 = ReLU()(batch_norm1)

    # Convolutional block two
    conv2 = Conv2D(filters, kernel_size=(3,3), padding="same")(activation1)
    batch_norm2 = BatchNormalization()(conv2)
    activation2 = ReLU()(batch_norm2)

    return activation2

def encoder(entered_input, filters=64):
    enc = convolutional_operaration(entered_input, filters)
    maxpo = MaxPooling2D(strides=(2,2))(enc)
    return enc, maxpo

def decoder(entered_input, skip, filters=64):
    upsample = Conv2DTranspose(filters, (2,2), strides=2, padding="same")(entered_input)
    connection = Concatenate()([upsample, skip])
    out = convolutional_operaration(connection, filters)
    return out

def U_net(imagesize):

    inputs = Input(imagesize)

    # encoding phase
    skip_1, encoder_1 = encoder(inputs, filters=64)
    skip_2, encoder_2 = encoder(encoder_1, filters=64*2)
    skip_3, encoder_3 = encoder(encoder_2, filters=64*4)
    skip_4, encoder_4 = encoder(encoder_3, filters=64*8)

    # Bottom U
    convolutioal = convolutional_operaration(encoder_4, filters=64*16)

    # decoding phase
    decoder_1 = decoder(convolutioal, skip_4, filters=64*8)
    decoder_2 = decoder(decoder_1, skip_3, filters=64*4)
    decoder_3 = decoder(decoder_2, skip_2, filters=64*2)
    decoder_4 = decoder(decoder_3, skip_1, filters=64)

    out = Conv2D(1, 1, padding="same", activation="sigmoid")(decoder_4)

    model = Model(inputs, out)

    return model

def callback(name):
    return [
        keras.callbacks.ModelCheckpoint(
            name,
            monitor="val_loss",
            verbose=0,
            save_best_only=True,
            save_weights_only=False,
            mode="auto",
            save_freq="epoch",
            initial_value_threshold=None,
        )
    ]

def load_model(path):
    return keras.models.load_model(path, compile=True)

def train(shape, learning_rate, epochs,
          callbacks, seq_train, seg_train,
          seq_val, seg_val, batch_size):
    
    input_shape = shape

    model = U_net(input_shape)

    model.compile(
        optimizer=keras.optimizers.RMSprop(
        learning_rate=learning_rate),
        loss="binary_crossentropy")

    history = model.fit(seq_train, seg_train,
                    epochs=epochs,
                    validation_data=(seq_val, seg_val),
                    callbacks=callbacks,
                    batch_size=batch_size)

    return history

def eval(model, input_files, output_directory):

    for file in input_files:
        # read sequence
        data, _ = nrrd.read(str(file))

        # define path for writing probilities to
        proba_out = Path(output_directory)/Path(file.stem + ".seg.nrrd")

        # predict kidney cortex
        predictions = model.predict(data)

        # write file to specified directory
        nrrd.write(str(proba_out), predictions)

    return 0


if __name__ == "__main__":
    args = parser.parse_args()

    # training mode
    if args.train and \
        args.epochs and args.shape\
        and args.learning_rate and \
            args.batch_size and \
            args.model_name and \
            args.training_data:
        
        # parse hyperparameters
        X, Y, c = args.shape.split(";")
        epochs = args.epochs
        learning_rate = args.learning_rate
        name = args.model_name
        batch_size = args.batch_size

        # load input data
        f_in = args.training_data
        with open(f_in, "+br") as p_in:
            data = pickle.load(p_in)

        # configure callback
        callb = callback(name)

        # train model
        history = train(callbacks=callb,
                        shape=(int(X), int(Y), int(c),),
                        epochs=epochs,
                        learning_rate=learning_rate,
                        seq_train=data["seq_train"],
                        seg_train=data["seg_train"],
                        seq_val=data["seq_val"], 
                        seg_val=data["seg_val"],
                        batch_size=batch_size)
        
        # save history
        with open(f"{name}_training_history.pkl", "+bw") as p_out:
            pickle.dump(history, p_out)

    # predicting mode
    elif args.predict and not args.train and\
        args.input_directory and args.output_directory:   

        # get files from directory
        if "*" in str(args.input_directory):
            input_files = Path(".").glob(args.input_directory)
        else:
            input_files = Path(args.input_directory).glob("*.nrrd")

        # load model
        model = load_model(args.predict)

        # evaluate
        eval(model, input_files, args.output_directory)

    # something is not right
    else:
        parser.print_help()

