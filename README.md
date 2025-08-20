![image](https://pre-image.eu/wp-content/uploads/2019/12/PRE-IMAGE-logo-1-white-background-scaled.png)

# PREIMAGE-1 - Radiomics
Code repository for functional MRI radiogenomics project: **PREIMAGE-1**

## 📘 Table of Contents
- [Description](#-description-)
- [Get Started](#-get-started-)
- [Why](#-why-)
- [Get Started](#-get-started-)
- [Run](#-run-)
- [Abstract](#-abstract-)

## 📝 Description
This repository contains code and methods used by the **PREIMAGE-1** study. In this study, MRI scans are interpreted as a proxy for tissue sampling. This study makes use of deep-learning image segmentation, radiomics features and gradient boosting classification/ regression.

## ❓ Why? 
Objectively assessing the physiological state of donor kidneys is complicated. True methods of capturing the physiological state are invasive, damage the kidney and are impractical due to time restrains surounding the transplantation process. **PREIMAGE** aims to explore radiomics based solution for practical and objective tissue assesment.

## 🛫 Get Started
Get started by cloning the repository.

```{bash}
git clone https://github.com/jgray1996/mri_kidney_perfusion
```

Within the repository it is expected, relevant data is stored in a directory called `data`.

Install the right dependencies with conda through the `mri.yaml`

```{bash}
conda env create -f mri.yaml
``` 

## ⚙️ Run
### Create database
```{bash}
echo hi!
```

### Concatanate NRRD files
```{bash}
echo hi!
```

### Train U-NET
```{bash}
echo hi!
```

### Segment U-NET
```{bash}
echo hi!
```

### Post-process segmentation U-NET
```{bash}
panel serve interface/app.py
```



### Radiomics modeling
```{bash}
echo hi!
```

## 👨‍💻 Abstract
Kidney transplantation is constrained by limited donor availability and subjective evaluation criteria that risk discarding potentially viable organs. Normothermic machine perfusion (NMP) has emerged as a promising technique for preserving and functionally assessing donor kidneys, yet reliable, non-invasive biomarkers for viability remain limited. This study investigates the use of magnetic resonance imaging (MRI)–derived radiomics features, combined with deep learning segmentation and machine learning models, to characterize perfusion physiology and ischemic injury during ex vivo kidney perfusion in a porcine model. A U-Net architecture was implemented for automated renal cortex segmentation across multiple MRI sequences (T1, T2, T2*, DWI, ASL), enabling standardized feature extraction. Radiomics-based classification models successfully differentiated ischemia status, with diffusion-weighted imaging (DWI) and arterial spin labeling (ASL) features achieving the highest predictive performance (AUC = 0.88 and 0.85, respectively). Regression analysis of NMP duration in warm-ischemic kidneys yielded moderate predictive power (R2 = 0.46) from T2-derived features after feature selection. Results highlight that radiomics outperforms direct convolutional neural network classification on raw images and provides a reproducible, non-invasive pipeline for kidney assessment during NMP. While ischemia classification proved robust, prediction of continuous perfusion parameters remains challenging. These findings demonstrate the potential of radiomics and AI to improve donor kidney evaluation, reduce unnecessary discard, and ultimately support better transplantation outcomes.