# References

## Economic Theory

**Hardin, G. (1968).** "The Tragedy of the Commons." *Science*, 162(3859), 1243–1248.
> The foundational paper on shared resource depletion. The free rider problem in AI subscription products is a direct instantiation of this dynamic.

**Olson, M. (1965).** *The Logic of Collective Action.* Harvard University Press.
> Rigorous treatment of why rational individuals undercontribute to collective goods. Relevant to understanding why multi-account abuse is individually rational while collectively harmful.

**Varian, H. (1994).** "Sequential provision of public goods." *Journal of Public Economics*, 53(2), 165–186.
> On sequential free riding and commitment problems — applicable to free tier cycling behavior.

---

## Fraud and Abuse Detection

**Stripe. (2026).** *Global Fraud Report: First-Party Fraud Trends.*
> Source for the ~20% first-party fraud rate estimate used as the abuse base rate in this project. First-party fraud (friendly fraud) is the closest published analog to subscription abuse.

**Akoglu, L., Tong, H., & Koutra, D. (2015).** "Graph-based Anomaly Detection and Description: A Survey." *Data Mining and Knowledge Discovery*, 29(3), 626–688.
> Graph-based approaches to detecting linked accounts — directly applicable to cluster-based abuse detection.

**Sánchez, D., Bilal, M., et al. (2020).** "A survey on anomaly detection for behavioral biometrics." *ACM Computing Surveys*.
> Background on behavioral fingerprinting, the ML approach used in `ml_based.ipynb`.

---

## Labeling and Ground Truth

**Ratner, A., et al. (2017).** "Snorkel: Rapid Training Data Creation with Weak Supervision." *VLDB 2017*.
> Programmatic labeling approach that formalizes the proxy label problem discussed in `why_definition_is_the_hard_part.md`. Relevant for scaling label creation.

**Northcutt, C., Athalye, A., & Mueller, J. (2021).** "Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks." *NeurIPS 2021*.
> Empirical evidence that label noise is pervasive and systematically biases model evaluation — directly relevant to the argument against binary `is_abuse` labels.

---

## Machine Learning Methods

**Lundberg, S. M., & Lee, S.-I. (2017).** "A Unified Approach to Interpreting Model Predictions." *NeurIPS 2017*.
> SHAP values. Used in `ml_based.ipynb` for explainability analysis.
> [https://github.com/slundberg/shap](https://github.com/slundberg/shap)

**Chen, T., & Guestrin, C. (2016).** "XGBoost: A Scalable Tree Boosting System." *KDD 2016*.
> The gradient boosting implementation used throughout the detection notebooks.

**Davis, J., & Goadrich, M. (2006).** "The Relationship Between Precision-Recall and ROC Curves." *ICML 2006*.
> Justification for using precision-recall curves rather than ROC-AUC under class imbalance — directly applicable to abuse detection datasets with ~80% clean accounts.

---

## Datasets

**DAS Group. (2023).** *Risk-Based Authentication (RBA) Dataset.* Kaggle.
> [https://www.kaggle.com/datasets/dasgroup/rba-dataset](https://www.kaggle.com/datasets/dasgroup/rba-dataset)
> Source of device fingerprint data used in the simulation layer.

---

## Industry Context

**OpenAI. (2023–2026).** *ChatGPT usage policy and free tier structure changes.*
> OpenAI has publicly documented multiple changes to free tier access limits in response to observed gaming behavior.

**GPTZero. (2024).** *Trust & Safety blog posts on multi-account detection.*
> GPTZero has publicly described student multi-account abuse as a material operational problem.

**Anthropic. (2024).** *Claude usage policy.*
> [https://www.anthropic.com/legal/usage-policy](https://www.anthropic.com/legal/usage-policy)
> Defines prohibited uses including circumventing access controls, which encompasses free tier cycling.

---

## Further Reading

**Savage, S., & Voelker, G. (2014).** "Measuring Merchant Vulnerability to Fraudulent Returns." *USENIX Security.*
> Measurement methodology for hard-to-observe fraud behaviors — analogous to measuring subscription abuse.

**Thomas, K., et al. (2013).** "Trafficking Fraudulent Accounts: The Role of the Underground Market in Twitter Spam and Abuse." *USENIX Security.*
> Case study in ecosystem-level thinking about account abuse — useful framing for ghost account supply chains.
