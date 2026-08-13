# Research report

Run ID: `20260811T162016Z_d2881b85`
Rows (cleaned): 104,810
Sources: ['trec5', 'trec6', 'trec7']

## 1. Executive finding
- Best random macro-F1: 0.986 (M2 character TF-IDF + linear SVM)
- Best source-disjoint macro-F1: 0.926 (A1 word TF-IDF (tokens removed) + logistic regression)
- Gap (random - source-disjoint): +0.060
- Conventional random splitting overestimates cross-source performance in this corpus.

## 2. Dataset audit
See `outputs/audit/audit_summary.md` and `outputs/audit/` tables.

## 3. Split validity
- `random_seed42`: protocol=random, train=83,848, test=20,962, held-out=[]
- `random_seed7`: protocol=random, train=83,848, test=20,962, held-out=[]
- `random_seed123`: protocol=random, train=83,848, test=20,962, held-out=[]
- `holdout_trec5_trec7`: protocol=source_disjoint, train=14,696, test=90,114, held-out=['trec5', 'trec7']
- `random_seed42_eq_holdout_trec5_trec7`: protocol=random, train=14,696, test=90,114, held-out=[]
- `random_seed42_fullmatch_holdout_trec5_trec7`: protocol=random, train=14,696, test=90,114, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec5_trec7`: protocol=random_cluster_disjoint_pooled, train=13,946, test=90,864, held-out=[]
- `cluster_disjoint_holdout_trec5_trec7`: protocol=cluster_disjoint, train=14,252, test=85,621, held-out=['trec5', 'trec7']
- `joint_source_cluster_disjoint_holdout_trec5_trec7`: protocol=joint_source_cluster_disjoint, train=14,252, test=85,621, held-out=['trec5', 'trec7']
- `holdout_trec6_trec7`: protocol=source_disjoint, train=46,762, test=58,048, held-out=['trec6', 'trec7']
- `random_seed42_eq_holdout_trec6_trec7`: protocol=random, train=46,762, test=58,048, held-out=[]
- `random_seed42_fullmatch_holdout_trec6_trec7`: protocol=random, train=46,762, test=58,048, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec6_trec7`: protocol=random_cluster_disjoint_pooled, train=44,337, test=60,473, held-out=[]
- `cluster_disjoint_holdout_trec6_trec7`: protocol=cluster_disjoint, train=43,275, test=56,500, held-out=['trec6', 'trec7']
- `joint_source_cluster_disjoint_holdout_trec6_trec7`: protocol=joint_source_cluster_disjoint, train=43,275, test=56,500, held-out=['trec6', 'trec7']
- `holdout_trec7`: protocol=source_disjoint, train=61,458, test=43,352, held-out=['trec7']
- `random_seed42_eq_holdout_trec7`: protocol=random, train=61,458, test=43,352, held-out=[]
- `random_seed42_fullmatch_holdout_trec7`: protocol=random, train=61,458, test=43,352, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec7`: protocol=random_cluster_disjoint_pooled, train=61,109, test=43,701, held-out=[]
- `cluster_disjoint_holdout_trec7`: protocol=cluster_disjoint, train=57,723, test=42,165, held-out=['trec7']
- `joint_source_cluster_disjoint_holdout_trec7`: protocol=joint_source_cluster_disjoint, train=57,723, test=42,165, held-out=['trec7']
- `holdout_trec5`: protocol=source_disjoint, train=58,048, test=46,762, held-out=['trec5']
- `random_seed42_eq_holdout_trec5`: protocol=random, train=58,048, test=46,762, held-out=[]
- `random_seed42_fullmatch_holdout_trec5`: protocol=random, train=58,048, test=46,762, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec5`: protocol=random_cluster_disjoint_pooled, train=60,522, test=44,288, held-out=[]
- `cluster_disjoint_holdout_trec5`: protocol=cluster_disjoint, train=56,500, test=43,275, held-out=['trec5']
- `joint_source_cluster_disjoint_holdout_trec5`: protocol=joint_source_cluster_disjoint, train=56,500, test=43,275, held-out=['trec5']
- `holdout_trec5_trec6`: protocol=source_disjoint, train=43,352, test=61,458, held-out=['trec5', 'trec6']
- `random_seed42_eq_holdout_trec5_trec6`: protocol=random, train=43,352, test=61,458, held-out=[]
- `random_seed42_fullmatch_holdout_trec5_trec6`: protocol=random, train=43,352, test=61,458, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec5_trec6`: protocol=random_cluster_disjoint_pooled, train=44,247, test=60,563, held-out=[]
- `cluster_disjoint_holdout_trec5_trec6`: protocol=cluster_disjoint, train=42,165, test=57,723, held-out=['trec5', 'trec6']
- `joint_source_cluster_disjoint_holdout_trec5_trec6`: protocol=joint_source_cluster_disjoint, train=42,165, test=57,723, held-out=['trec5', 'trec6']
- `holdout_trec6`: protocol=source_disjoint, train=90,114, test=14,696, held-out=['trec6']
- `random_seed42_eq_holdout_trec6`: protocol=random, train=90,114, test=14,696, held-out=[]
- `random_seed42_fullmatch_holdout_trec6`: protocol=random, train=90,114, test=14,696, held-out=[]
- `random_cluster_disjoint_pooled_holdout_trec6`: protocol=random_cluster_disjoint_pooled, train=90,856, test=13,954, held-out=[]
- `cluster_disjoint_holdout_trec6`: protocol=cluster_disjoint, train=85,621, test=14,252, held-out=['trec6']
- `joint_source_cluster_disjoint_holdout_trec6`: protocol=joint_source_cluster_disjoint, train=85,621, test=14,252, held-out=['trec6']
- `secondary_test`: protocol=secondary_test, train=83,848, test=20,069, held-out=['secondary']
- All leakage assertions passed (row-ID, text-hash, and source disjointness; both classes everywhere).

## 4. Main results
| split_id | protocol | model_id | macro_f1 | precision_pos | recall_pos | mcc |
| --- | --- | --- | --- | --- | --- | --- |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | character_linear_svm | 0.858 | 0.74 | 0.961 | 0.738 |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | character_noanon_linear_svm | 0.841 | 0.713 | 0.962 | 0.711 |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | structural_logistic_regression | 0.747 | 0.841 | 0.523 | 0.534 |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | word_logistic_regression | 0.826 | 0.693 | 0.957 | 0.685 |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | word_noanon_logistic_regression | 0.809 | 0.666 | 0.972 | 0.666 |
| cluster_disjoint_holdout_trec5 | cluster_disjoint | word_xgboost | 0.755 | 0.61 | 0.936 | 0.571 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | character_linear_svm | 0.666 | 0.5 | 0.977 | 0.483 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | character_noanon_linear_svm | 0.651 | 0.488 | 0.981 | 0.468 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | structural_logistic_regression | 0.402 | 0.306 | 0.628 | -0.084 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | word_logistic_regression | 0.644 | 0.483 | 0.985 | 0.464 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | word_noanon_logistic_regression | 0.627 | 0.471 | 0.989 | 0.447 |
| cluster_disjoint_holdout_trec5_trec6 | cluster_disjoint | word_xgboost | 0.547 | 0.425 | 0.98 | 0.355 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | character_linear_svm | 0.889 | 0.863 | 0.903 | 0.779 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | character_noanon_linear_svm | 0.881 | 0.847 | 0.906 | 0.764 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | structural_logistic_regression | 0.772 | 0.76 | 0.741 | 0.543 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | word_logistic_regression | 0.875 | 0.842 | 0.897 | 0.752 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | word_noanon_logistic_regression | 0.863 | 0.82 | 0.9 | 0.73 |
| cluster_disjoint_holdout_trec5_trec7 | cluster_disjoint | word_xgboost | 0.829 | 0.873 | 0.744 | 0.666 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | character_linear_svm | 0.886 | 0.733 | 0.956 | 0.786 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | character_noanon_linear_svm | 0.891 | 0.744 | 0.954 | 0.794 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | structural_logistic_regression | 0.723 | 0.592 | 0.532 | 0.447 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | word_logistic_regression | 0.907 | 0.779 | 0.957 | 0.822 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | word_noanon_logistic_regression | 0.915 | 0.805 | 0.949 | 0.836 |
| cluster_disjoint_holdout_trec6 | cluster_disjoint | word_xgboost | 0.849 | 0.669 | 0.926 | 0.718 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | character_linear_svm | 0.843 | 0.79 | 0.908 | 0.695 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | character_noanon_linear_svm | 0.854 | 0.809 | 0.904 | 0.713 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | structural_logistic_regression | 0.621 | 0.575 | 0.8 | 0.287 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | word_logistic_regression | 0.849 | 0.797 | 0.91 | 0.705 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | word_noanon_logistic_regression | 0.865 | 0.835 | 0.889 | 0.731 |
| cluster_disjoint_holdout_trec6_trec7 | cluster_disjoint | word_xgboost | 0.781 | 0.735 | 0.838 | 0.569 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | character_linear_svm | 0.898 | 0.918 | 0.899 | 0.797 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | character_noanon_linear_svm | 0.904 | 0.929 | 0.898 | 0.809 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | structural_logistic_regression | 0.608 | 0.635 | 0.797 | 0.244 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | word_logistic_regression | 0.886 | 0.9 | 0.898 | 0.773 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | word_noanon_logistic_regression | 0.886 | 0.901 | 0.894 | 0.771 |
| cluster_disjoint_holdout_trec7 | cluster_disjoint | word_xgboost | 0.838 | 0.889 | 0.812 | 0.681 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | character_linear_svm | 0.858 | 0.74 | 0.961 | 0.738 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.841 | 0.713 | 0.962 | 0.711 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | structural_logistic_regression | 0.747 | 0.841 | 0.523 | 0.534 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | word_logistic_regression | 0.826 | 0.693 | 0.957 | 0.685 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.809 | 0.666 | 0.972 | 0.666 |
| joint_source_cluster_disjoint_holdout_trec5 | joint_source_cluster_disjoint | word_xgboost | 0.755 | 0.61 | 0.936 | 0.571 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | character_linear_svm | 0.666 | 0.5 | 0.977 | 0.483 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.651 | 0.488 | 0.981 | 0.468 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | structural_logistic_regression | 0.402 | 0.306 | 0.628 | -0.084 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | word_logistic_regression | 0.644 | 0.483 | 0.985 | 0.464 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.627 | 0.471 | 0.989 | 0.447 |
| joint_source_cluster_disjoint_holdout_trec5_trec6 | joint_source_cluster_disjoint | word_xgboost | 0.547 | 0.425 | 0.98 | 0.355 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | character_linear_svm | 0.889 | 0.863 | 0.903 | 0.779 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.881 | 0.847 | 0.906 | 0.764 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | structural_logistic_regression | 0.772 | 0.76 | 0.741 | 0.543 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | word_logistic_regression | 0.875 | 0.842 | 0.897 | 0.752 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.863 | 0.82 | 0.9 | 0.73 |
| joint_source_cluster_disjoint_holdout_trec5_trec7 | joint_source_cluster_disjoint | word_xgboost | 0.829 | 0.873 | 0.744 | 0.666 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | character_linear_svm | 0.886 | 0.733 | 0.956 | 0.786 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.891 | 0.744 | 0.954 | 0.794 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | structural_logistic_regression | 0.723 | 0.592 | 0.532 | 0.447 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | word_logistic_regression | 0.907 | 0.779 | 0.957 | 0.822 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.915 | 0.805 | 0.949 | 0.836 |
| joint_source_cluster_disjoint_holdout_trec6 | joint_source_cluster_disjoint | word_xgboost | 0.849 | 0.669 | 0.926 | 0.718 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | character_linear_svm | 0.843 | 0.79 | 0.908 | 0.695 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.854 | 0.809 | 0.904 | 0.713 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | structural_logistic_regression | 0.621 | 0.575 | 0.8 | 0.287 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | word_logistic_regression | 0.849 | 0.797 | 0.91 | 0.705 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.865 | 0.835 | 0.889 | 0.731 |
| joint_source_cluster_disjoint_holdout_trec6_trec7 | joint_source_cluster_disjoint | word_xgboost | 0.781 | 0.735 | 0.838 | 0.569 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | character_linear_svm | 0.898 | 0.918 | 0.899 | 0.797 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | character_noanon_linear_svm | 0.904 | 0.929 | 0.898 | 0.809 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | structural_logistic_regression | 0.608 | 0.635 | 0.797 | 0.244 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | word_logistic_regression | 0.886 | 0.9 | 0.898 | 0.773 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | word_noanon_logistic_regression | 0.886 | 0.901 | 0.894 | 0.771 |
| joint_source_cluster_disjoint_holdout_trec7 | joint_source_cluster_disjoint | word_xgboost | 0.838 | 0.889 | 0.812 | 0.681 |
| random_seed123 | random | character_linear_svm | 0.986 | 0.984 | 0.985 | 0.972 |
| random_seed123 | random | character_noanon_linear_svm | 0.985 | 0.982 | 0.985 | 0.97 |
| random_seed123 | random | structural_logistic_regression | 0.804 | 0.87 | 0.681 | 0.624 |
| random_seed123 | random | word_logistic_regression | 0.981 | 0.975 | 0.984 | 0.963 |
| random_seed123 | random | word_noanon_logistic_regression | 0.98 | 0.975 | 0.982 | 0.961 |
| random_seed123 | random | word_xgboost | 0.959 | 0.957 | 0.952 | 0.918 |
| random_seed42 | random | character_linear_svm | 0.986 | 0.982 | 0.987 | 0.972 |
| random_seed42 | random | character_noanon_linear_svm | 0.984 | 0.979 | 0.985 | 0.968 |
| random_seed42 | random | structural_logistic_regression | 0.804 | 0.864 | 0.686 | 0.622 |
| random_seed42 | random | word_logistic_regression | 0.982 | 0.976 | 0.985 | 0.964 |
| random_seed42 | random | word_noanon_logistic_regression | 0.981 | 0.974 | 0.984 | 0.962 |
| random_seed42 | random | word_xgboost | 0.959 | 0.955 | 0.953 | 0.917 |
| random_seed42_eq_holdout_trec5 | random | character_linear_svm | 0.984 | 0.98 | 0.985 | 0.969 |
| random_seed42_eq_holdout_trec5 | random | character_noanon_linear_svm | 0.983 | 0.979 | 0.983 | 0.966 |
| random_seed42_eq_holdout_trec5 | random | structural_logistic_regression | 0.802 | 0.864 | 0.682 | 0.62 |
| random_seed42_eq_holdout_trec5 | random | word_logistic_regression | 0.98 | 0.973 | 0.982 | 0.959 |
| random_seed42_eq_holdout_trec5 | random | word_noanon_logistic_regression | 0.978 | 0.971 | 0.98 | 0.956 |
| random_seed42_eq_holdout_trec5 | random | word_xgboost | 0.96 | 0.956 | 0.955 | 0.92 |
| random_seed42_eq_holdout_trec5_trec6 | random | character_linear_svm | 0.984 | 0.98 | 0.984 | 0.968 |
| random_seed42_eq_holdout_trec5_trec6 | random | character_noanon_linear_svm | 0.982 | 0.979 | 0.982 | 0.965 |
| random_seed42_eq_holdout_trec5_trec6 | random | structural_logistic_regression | 0.803 | 0.867 | 0.681 | 0.621 |
| random_seed42_eq_holdout_trec5_trec6 | random | word_logistic_regression | 0.978 | 0.973 | 0.979 | 0.956 |
| random_seed42_eq_holdout_trec5_trec6 | random | word_noanon_logistic_regression | 0.977 | 0.971 | 0.977 | 0.953 |
| random_seed42_eq_holdout_trec5_trec6 | random | word_xgboost | 0.959 | 0.958 | 0.952 | 0.919 |
| random_seed42_eq_holdout_trec5_trec7 | random | character_linear_svm | 0.977 | 0.972 | 0.978 | 0.954 |
| random_seed42_eq_holdout_trec5_trec7 | random | character_noanon_linear_svm | 0.977 | 0.971 | 0.977 | 0.953 |
| random_seed42_eq_holdout_trec5_trec7 | random | structural_logistic_regression | 0.802 | 0.864 | 0.681 | 0.619 |
| random_seed42_eq_holdout_trec5_trec7 | random | word_logistic_regression | 0.971 | 0.968 | 0.968 | 0.943 |
| random_seed42_eq_holdout_trec5_trec7 | random | word_noanon_logistic_regression | 0.969 | 0.964 | 0.969 | 0.939 |
| random_seed42_eq_holdout_trec5_trec7 | random | word_xgboost | 0.954 | 0.952 | 0.947 | 0.909 |
| random_seed42_eq_holdout_trec6 | random | character_linear_svm | 0.986 | 0.982 | 0.986 | 0.972 |
| random_seed42_eq_holdout_trec6 | random | character_noanon_linear_svm | 0.983 | 0.978 | 0.985 | 0.966 |
| random_seed42_eq_holdout_trec6 | random | structural_logistic_regression | 0.805 | 0.867 | 0.687 | 0.626 |
| random_seed42_eq_holdout_trec6 | random | word_logistic_regression | 0.982 | 0.976 | 0.985 | 0.965 |
| random_seed42_eq_holdout_trec6 | random | word_noanon_logistic_regression | 0.981 | 0.974 | 0.983 | 0.962 |
| random_seed42_eq_holdout_trec6 | random | word_xgboost | 0.96 | 0.957 | 0.956 | 0.921 |
| random_seed42_eq_holdout_trec6_trec7 | random | character_linear_svm | 0.984 | 0.98 | 0.985 | 0.968 |
| random_seed42_eq_holdout_trec6_trec7 | random | character_noanon_linear_svm | 0.982 | 0.979 | 0.982 | 0.965 |
| random_seed42_eq_holdout_trec6_trec7 | random | structural_logistic_regression | 0.802 | 0.865 | 0.681 | 0.62 |
| random_seed42_eq_holdout_trec6_trec7 | random | word_logistic_regression | 0.978 | 0.973 | 0.979 | 0.957 |
| random_seed42_eq_holdout_trec6_trec7 | random | word_noanon_logistic_regression | 0.977 | 0.971 | 0.978 | 0.954 |
| random_seed42_eq_holdout_trec6_trec7 | random | word_xgboost | 0.959 | 0.956 | 0.953 | 0.918 |
| random_seed42_eq_holdout_trec7 | random | character_linear_svm | 0.984 | 0.98 | 0.986 | 0.969 |
| random_seed42_eq_holdout_trec7 | random | character_noanon_linear_svm | 0.983 | 0.979 | 0.983 | 0.966 |
| random_seed42_eq_holdout_trec7 | random | structural_logistic_regression | 0.801 | 0.863 | 0.68 | 0.617 |
| random_seed42_eq_holdout_trec7 | random | word_logistic_regression | 0.98 | 0.974 | 0.982 | 0.96 |
| random_seed42_eq_holdout_trec7 | random | word_noanon_logistic_regression | 0.979 | 0.972 | 0.981 | 0.957 |
| random_seed42_eq_holdout_trec7 | random | word_xgboost | 0.959 | 0.957 | 0.952 | 0.918 |
| random_seed42_fullmatch_holdout_trec5 | random | character_linear_svm | 0.985 | 0.978 | 0.986 | 0.969 |
| random_seed42_fullmatch_holdout_trec5 | random | character_noanon_linear_svm | 0.984 | 0.977 | 0.985 | 0.967 |
| random_seed42_fullmatch_holdout_trec5 | random | structural_logistic_regression | 0.806 | 0.855 | 0.677 | 0.626 |
| random_seed42_fullmatch_holdout_trec5 | random | word_logistic_regression | 0.979 | 0.971 | 0.98 | 0.959 |
| random_seed42_fullmatch_holdout_trec5 | random | word_noanon_logistic_regression | 0.978 | 0.969 | 0.98 | 0.957 |
| random_seed42_fullmatch_holdout_trec5 | random | word_xgboost | 0.96 | 0.947 | 0.959 | 0.919 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | character_linear_svm | 0.982 | 0.969 | 0.986 | 0.965 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | character_noanon_linear_svm | 0.981 | 0.967 | 0.985 | 0.962 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | structural_logistic_regression | 0.809 | 0.833 | 0.675 | 0.627 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | word_logistic_regression | 0.977 | 0.962 | 0.98 | 0.953 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | word_noanon_logistic_regression | 0.975 | 0.958 | 0.979 | 0.95 |
| random_seed42_fullmatch_holdout_trec5_trec6 | random | word_xgboost | 0.955 | 0.92 | 0.97 | 0.91 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | character_linear_svm | 0.975 | 0.983 | 0.965 | 0.951 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | character_noanon_linear_svm | 0.974 | 0.982 | 0.963 | 0.947 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | structural_logistic_regression | 0.798 | 0.88 | 0.682 | 0.616 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | word_logistic_regression | 0.97 | 0.975 | 0.962 | 0.94 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | word_noanon_logistic_regression | 0.969 | 0.974 | 0.961 | 0.938 |
| random_seed42_fullmatch_holdout_trec5_trec7 | random | word_xgboost | 0.935 | 0.982 | 0.882 | 0.874 |
| random_seed42_fullmatch_holdout_trec6 | random | character_linear_svm | 0.982 | 0.958 | 0.988 | 0.964 |
| random_seed42_fullmatch_holdout_trec6 | random | character_noanon_linear_svm | 0.981 | 0.955 | 0.987 | 0.962 |
| random_seed42_fullmatch_holdout_trec6 | random | structural_logistic_regression | 0.81 | 0.729 | 0.687 | 0.62 |
| random_seed42_fullmatch_holdout_trec6 | random | word_logistic_regression | 0.976 | 0.942 | 0.985 | 0.952 |
| random_seed42_fullmatch_holdout_trec6 | random | word_noanon_logistic_regression | 0.975 | 0.941 | 0.984 | 0.951 |
| random_seed42_fullmatch_holdout_trec6 | random | word_xgboost | 0.949 | 0.888 | 0.963 | 0.9 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | character_linear_svm | 0.984 | 0.983 | 0.983 | 0.968 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | character_noanon_linear_svm | 0.983 | 0.982 | 0.982 | 0.966 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | structural_logistic_regression | 0.799 | 0.885 | 0.675 | 0.62 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | word_logistic_regression | 0.979 | 0.978 | 0.978 | 0.958 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | word_noanon_logistic_regression | 0.978 | 0.976 | 0.978 | 0.956 |
| random_seed42_fullmatch_holdout_trec6_trec7 | random | word_xgboost | 0.958 | 0.965 | 0.945 | 0.915 |
| random_seed42_fullmatch_holdout_trec7 | random | character_linear_svm | 0.985 | 0.989 | 0.984 | 0.97 |
| random_seed42_fullmatch_holdout_trec7 | random | character_noanon_linear_svm | 0.984 | 0.989 | 0.982 | 0.968 |
| random_seed42_fullmatch_holdout_trec7 | random | structural_logistic_regression | 0.782 | 0.908 | 0.676 | 0.597 |
| random_seed42_fullmatch_holdout_trec7 | random | word_logistic_regression | 0.98 | 0.985 | 0.979 | 0.96 |
| random_seed42_fullmatch_holdout_trec7 | random | word_noanon_logistic_regression | 0.979 | 0.984 | 0.978 | 0.958 |
| random_seed42_fullmatch_holdout_trec7 | random | word_xgboost | 0.953 | 0.978 | 0.936 | 0.906 |
| random_seed7 | random | character_linear_svm | 0.986 | 0.982 | 0.987 | 0.971 |
| random_seed7 | random | character_noanon_linear_svm | 0.985 | 0.981 | 0.985 | 0.97 |
| random_seed7 | random | structural_logistic_regression | 0.807 | 0.873 | 0.685 | 0.63 |
| random_seed7 | random | word_logistic_regression | 0.982 | 0.976 | 0.983 | 0.963 |
| random_seed7 | random | word_noanon_logistic_regression | 0.98 | 0.974 | 0.982 | 0.96 |
| random_seed7 | random | word_xgboost | 0.961 | 0.957 | 0.956 | 0.922 |
| secondary_test | random | character_linear_svm | 0.858 | 0.759 | 0.931 | 0.729 |
| secondary_test | random | character_noanon_linear_svm | 0.887 | 0.836 | 0.893 | 0.776 |
| secondary_test | random | structural_logistic_regression | 0.281 | 0.381 | 0.991 | -0.016 |
| secondary_test | random | word_logistic_regression | 0.881 | 0.791 | 0.946 | 0.772 |
| secondary_test | random | word_noanon_logistic_regression | 0.896 | 0.839 | 0.913 | 0.794 |
| secondary_test | random | word_xgboost | 0.787 | 0.665 | 0.903 | 0.605 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | character_linear_svm | 0.983 | 0.976 | 0.984 | 0.967 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.982 | 0.974 | 0.982 | 0.965 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.797 | 0.843 | 0.648 | 0.61 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | word_logistic_regression | 0.978 | 0.97 | 0.977 | 0.956 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.977 | 0.967 | 0.976 | 0.953 |
| random_cluster_disjoint_pooled_holdout_trec5 | random_cluster_disjoint_pooled | word_xgboost | 0.956 | 0.94 | 0.954 | 0.913 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | character_linear_svm | 0.981 | 0.969 | 0.983 | 0.963 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.98 | 0.967 | 0.983 | 0.961 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.799 | 0.82 | 0.652 | 0.608 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | word_logistic_regression | 0.975 | 0.961 | 0.975 | 0.951 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.973 | 0.959 | 0.973 | 0.947 |
| random_cluster_disjoint_pooled_holdout_trec5_trec6 | random_cluster_disjoint_pooled | word_xgboost | 0.952 | 0.914 | 0.967 | 0.906 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | character_linear_svm | 0.974 | 0.983 | 0.963 | 0.948 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.972 | 0.982 | 0.96 | 0.945 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.79 | 0.854 | 0.689 | 0.594 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | word_logistic_regression | 0.97 | 0.973 | 0.965 | 0.94 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.968 | 0.972 | 0.962 | 0.937 |
| random_cluster_disjoint_pooled_holdout_trec5_trec7 | random_cluster_disjoint_pooled | word_xgboost | 0.931 | 0.984 | 0.873 | 0.868 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | character_linear_svm | 0.98 | 0.952 | 0.985 | 0.959 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.978 | 0.947 | 0.984 | 0.956 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.801 | 0.702 | 0.669 | 0.602 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | word_logistic_regression | 0.973 | 0.936 | 0.982 | 0.947 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.972 | 0.934 | 0.98 | 0.945 |
| random_cluster_disjoint_pooled_holdout_trec6 | random_cluster_disjoint_pooled | word_xgboost | 0.944 | 0.872 | 0.959 | 0.89 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | character_linear_svm | 0.984 | 0.984 | 0.984 | 0.969 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.983 | 0.983 | 0.982 | 0.966 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.8 | 0.881 | 0.691 | 0.618 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | word_logistic_regression | 0.98 | 0.978 | 0.981 | 0.96 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.978 | 0.976 | 0.979 | 0.956 |
| random_cluster_disjoint_pooled_holdout_trec6_trec7 | random_cluster_disjoint_pooled | word_xgboost | 0.959 | 0.968 | 0.947 | 0.918 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | character_linear_svm | 0.985 | 0.989 | 0.984 | 0.97 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | character_noanon_linear_svm | 0.984 | 0.989 | 0.983 | 0.968 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | structural_logistic_regression | 0.785 | 0.911 | 0.685 | 0.601 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | word_logistic_regression | 0.981 | 0.985 | 0.981 | 0.961 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | word_noanon_logistic_regression | 0.979 | 0.984 | 0.98 | 0.959 |
| random_cluster_disjoint_pooled_holdout_trec7 | random_cluster_disjoint_pooled | word_xgboost | 0.953 | 0.978 | 0.939 | 0.908 |
| holdout_trec5 | source_disjoint | character_linear_svm | 0.868 | 0.773 | 0.967 | 0.756 |
| holdout_trec5 | source_disjoint | character_noanon_linear_svm | 0.854 | 0.751 | 0.968 | 0.732 |
| holdout_trec5 | source_disjoint | structural_logistic_regression | 0.764 | 0.882 | 0.563 | 0.571 |
| holdout_trec5 | source_disjoint | word_logistic_regression | 0.841 | 0.734 | 0.964 | 0.71 |
| holdout_trec5 | source_disjoint | word_noanon_logistic_regression | 0.825 | 0.709 | 0.976 | 0.691 |
| holdout_trec5 | source_disjoint | word_xgboost | 0.772 | 0.655 | 0.945 | 0.597 |
| holdout_trec5_trec6 | source_disjoint | character_linear_svm | 0.685 | 0.542 | 0.982 | 0.508 |
| holdout_trec5_trec6 | source_disjoint | character_noanon_linear_svm | 0.671 | 0.531 | 0.984 | 0.492 |
| holdout_trec5_trec6 | source_disjoint | structural_logistic_regression | 0.416 | 0.348 | 0.649 | -0.072 |
| holdout_trec5_trec6 | source_disjoint | word_logistic_regression | 0.665 | 0.527 | 0.988 | 0.488 |
| holdout_trec5_trec6 | source_disjoint | word_noanon_logistic_regression | 0.649 | 0.516 | 0.991 | 0.472 |
| holdout_trec5_trec6 | source_disjoint | word_xgboost | 0.567 | 0.466 | 0.979 | 0.37 |
| holdout_trec5_trec7 | source_disjoint | character_linear_svm | 0.894 | 0.875 | 0.908 | 0.788 |
| holdout_trec5_trec7 | source_disjoint | character_noanon_linear_svm | 0.886 | 0.86 | 0.912 | 0.774 |
| holdout_trec5_trec7 | source_disjoint | structural_logistic_regression | 0.775 | 0.772 | 0.755 | 0.55 |
| holdout_trec5_trec7 | source_disjoint | word_logistic_regression | 0.882 | 0.861 | 0.899 | 0.764 |
| holdout_trec5_trec7 | source_disjoint | word_noanon_logistic_regression | 0.871 | 0.841 | 0.903 | 0.745 |
| holdout_trec5_trec7 | source_disjoint | word_xgboost | 0.838 | 0.878 | 0.774 | 0.681 |
| holdout_trec6 | source_disjoint | character_linear_svm | 0.895 | 0.759 | 0.96 | 0.802 |
| holdout_trec6 | source_disjoint | character_noanon_linear_svm | 0.9 | 0.769 | 0.958 | 0.81 |
| holdout_trec6 | source_disjoint | structural_logistic_regression | 0.751 | 0.679 | 0.555 | 0.508 |
| holdout_trec6 | source_disjoint | word_logistic_regression | 0.917 | 0.809 | 0.959 | 0.84 |
| holdout_trec6 | source_disjoint | word_noanon_logistic_regression | 0.926 | 0.834 | 0.952 | 0.855 |
| holdout_trec6 | source_disjoint | word_xgboost | 0.856 | 0.69 | 0.931 | 0.729 |
| holdout_trec6_trec7 | source_disjoint | character_linear_svm | 0.844 | 0.793 | 0.907 | 0.695 |
| holdout_trec6_trec7 | source_disjoint | character_noanon_linear_svm | 0.852 | 0.809 | 0.902 | 0.709 |
| holdout_trec6_trec7 | source_disjoint | structural_logistic_regression | 0.621 | 0.578 | 0.792 | 0.282 |
| holdout_trec6_trec7 | source_disjoint | word_logistic_regression | 0.854 | 0.811 | 0.901 | 0.712 |
| holdout_trec6_trec7 | source_disjoint | word_noanon_logistic_regression | 0.869 | 0.851 | 0.879 | 0.739 |
| holdout_trec6_trec7 | source_disjoint | word_xgboost | 0.774 | 0.725 | 0.845 | 0.558 |
| holdout_trec7 | source_disjoint | character_linear_svm | 0.898 | 0.918 | 0.897 | 0.796 |
| holdout_trec7 | source_disjoint | character_noanon_linear_svm | 0.903 | 0.93 | 0.893 | 0.806 |
| holdout_trec7 | source_disjoint | structural_logistic_regression | 0.592 | 0.624 | 0.775 | 0.209 |
| holdout_trec7 | source_disjoint | word_logistic_regression | 0.886 | 0.905 | 0.891 | 0.773 |
| holdout_trec7 | source_disjoint | word_noanon_logistic_regression | 0.886 | 0.907 | 0.887 | 0.772 |
| holdout_trec7 | source_disjoint | word_xgboost | 0.842 | 0.89 | 0.816 | 0.688 |

## 5. Efficiency
| model_id | feature_count | fit_time_s | inference_time_s_median | inference_time_s_per_1000 | serialized_size_mb | peak_mem_gb |
| --- | --- | --- | --- | --- | --- | --- |
| character_linear_svm | 100000.0 | 3.274 | 0.542 | 0.012 | 0.692 | 1.48 |
| character_noanon_linear_svm | 100000.0 | 3.129 | 0.515 | 0.012 | 0.693 | 1.36 |
| structural_logistic_regression | 210.0 | 0.551 | 0.011 | 0.0 | 0.002 | 0.02 |
| word_logistic_regression | 50000.0 | 1.863 | 0.079 | 0.002 | 0.362 | 0.22 |
| word_noanon_logistic_regression | 50000.0 | 1.839 | 0.068 | 0.002 | 0.362 | 0.21 |
| word_xgboost | 50000.0 | 111.297 | 1.271 | 0.027 | 0.086 | 2.24 |

## 6. Error analysis
- 300 sampled errors ({'false_positive': 150, 'false_negative': 150}).
See `error_samples_redacted.csv`; examples are redacted.

## 7. Limitations
See `reports/limitations.md`.

## 8. Reproducibility
See `reports/reproducibility.md`.

## 9. Recommended submission category
See `reports/submission_decision.md`.
