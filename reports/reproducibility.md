# Reproducibility report

> **Public repository:** https://github.com/Weihang-Huang/DeceptionEmail
>
> **Persistent DOI:** [Zenodo DOI to be added before final submission; reviewers may contact the corresponding author for early access to the camera-ready artifacts.]

- Run ID: `20260811T162016Z_d2881b85`
- Configuration hash: `c1e7d7c6e19165f19d4832a72c2426c4d5a0a64254681f792dc27e2b1fd6a945`
- Source-tree (code) hash: `4aa140d67f3683a0f1ad021ed88da24ec1fef860a159ad75ab9c85c098f914b2`
- Environment fingerprint: `0beb5708a0156167c44c5c16f755ee7deb0db018c33cf7b9d10ef1b5ba0acc1c`
- Commands:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements-lock.txt
  $env:PYTHONHASHSEED="42"; $env:OMP_NUM_THREADS="1"; $env:MKL_NUM_THREADS="1"; $env:OPENBLAS_NUM_THREADS="1"
  python -m pytest -q
  deceptive-email all --config configs/default.yaml
  ```

- Dataset: MeAJOR v2.0, DOI 10.5281/zenodo.18471483, parquet gzip, MD5 78e397ad8447bcdba5a98097921ba8bd, SHA-256 recorded in `outputs/audit/schema.json`.
- Secondary corpus: ealvaradob/phishing-dataset texts.json (Apache-2.0), 20,069 cleaned rows; exact-text overlap with MeAJOR is zero; 41 SimHash collisions.
- Resource use: `outputs/runs/<run_id>/logs/run_metadata.json` (timings, peak memory, hardware/package versions).
- Additional analyses (Phase C/D):
  ```powershell
  python scripts/run_secondary_audit.py
  python scripts/run_secondary_predictions.py
  python scripts/run_decomposition.py
  ```
- SimHash parameters: 64-bit SimHash over word tokens (md5 token hashing, sign-accumulated); 4 bands x 16 bits; exact duplicate groups at Hamming 0; near-duplicate pairs at Hamming <= 8 (LSH lower bound).
- Cluster-disjoint rule: exact-SimHash (Hamming 0) connected components; a component is assigned to train or test as a unit.
- Matched random controls: equal-size (test size matched) and fully matched (training size, test size, per-class counts, and seed matched).
- Cached-artifact map:
  ```json
{
  "run_id": "20260811T162016Z_d2881b85",
  "sources": {
    "dataset_hash": "0ccfd5bc0c14696909bc42cabee6c09836f6fef3b4655c845769d4d17a8f47ee",
    "config_hash": "c81a3d6cf62076efe34d663bb3c7ff91c00ed0d0725d9046d71d07f4014f8b72",
    "code_hash": "46891b04443524208c6b87e02ad5fc94d95f82ef966e8a093706b716f2878382",
    "env_hash": "1fdd632f08642dea901a7adf9238175ce54c79748f88268503b29839c591ee84",
    "split_hash": "48dcc084cfd0ebf47e1abaaa327afe62801e6c439e9c98ea9b5494f7c08a397a"
  },
  "environment": {
    "os": "Windows",
    "os_release": "11",
    "platform": "Windows-11-10.0.26100-SP0",
    "python": "3.13.2",
    "hostname": "DESKTOP-07538N8",
    "cpu": "Intel64 Family 6 Model 170 Stepping 4, GenuineIntel",
    "cpu_count_physical": 16,
    "cpu_count_logical": 22,
    "ram_total_gb": 95.5,
    "ram_available_gb": 68.76,
    "disk_free_gb": 179.86,
    "packages": {
      "pandas": "2.3.3",
      "pyarrow": "23.0.1",
      "numpy": "2.1.3",
      "scipy": "1.18.0",
      "scikit-learn": "1.9.0",
      "joblib": "1.5.3",
      "psutil": "7.2.2",
      "PyYAML": "6.0.2",
      "matplotlib": "3.11.0",
      "seaborn": "0.13.2",
      "pytest": "8.3.3"
    }
  },
  "matrix_keys": [
    {
      "split": "random_seed42",
      "rep": "word",
      "key": "8dc85d9014b56374fa9217d81769ffafbbf1101571b8b574dc6440bb48d3a46f"
    },
    {
      "split": "random_seed42",
      "rep": "character",
      "key": "befd128800195637ce3f5ae97e98aa3a980ef70c4cc6322f8a95b74885516319"
    },
    {
      "split": "random_seed42",
      "rep": "structural",
      "key": "7dddb7918da4a84a80f89f93fde2eb2d4c0aadaa5d2b122f17527731241681d7"
    },
    {
      "split": "random_seed42",
      "rep": "word",
      "key": "8dc85d9014b56374fa9217d81769ffafbbf1101571b8b574dc6440bb48d3a46f"
    },
    {
      "split": "random_seed42",
      "rep": "word_noanon",
      "key": "f9ad887e731884331c14bb5dacdae8139c508ee097cea9131a3525c1a781c1e1"
    },
    {
      "split": "random_seed42",
      "rep": "character_noanon",
      "key": "5ab1ed8c6a86b5b5cc8b3e1e4be620e4181936f6118c6fe117f65ac40f0ac7f4"
    },
    {
      "split": "random_seed7",
      "rep": "word",
      "key": "16c910ec0b51ad1417d584b61d96e677fdb7f0164534f361938b5e97028e4b2d"
    },
    {
      "split": "random_seed7",
      "rep": "character",
      "key": "00e618535019fc7f50d56901e430369ed1a475d2318ccea7b9f82825cb991c3a"
    },
    {
      "split": "random_seed7",
      "rep": "structural",
      "key": "feddc652b4bcbfd0ffd136d06ea87ec02001be5161bd398904b4af0d11b64496"
    },
    {
      "split": "random_seed7",
      "rep": "word",
      "key": "16c910ec0b51ad1417d584b61d96e677fdb7f0164534f361938b5e97028e4b2d"
    },
    {
      "split": "random_seed7",
      "rep": "word_noanon",
      "key": "32809ac00b1abfbabe6988e8a7fbf26d8dc34474b45e4524974f04424b5c0593"
    },
    {
      "split": "random_seed7",
      "rep": "character_noanon",
      "key": "c7ab63943693510e8a69bbcf17f48871c5461c4b9f2a9526c17fcf804d0a44b2"
    },
    {
      "split": "random_seed123",
      "rep": "word",
      "key": "489b80bb2e39381283a7154f732a498915faadac8ff9deccb41e9d7c13f28ccd"
    },
    {
      "split": "random_seed123",
      "rep": "character",
      "key": "f78bd889d8b8b992f8d20242bd3871b5aa1b4e8d5c040bcb3408bb31c4cbc130"
    },
    {
      "split": "random_seed123",
      "rep": "structural",
      "key": "af87b8130749606946985df3b944f65ba9958a052dcf31a1cf32dace90c4b236"
    },
    {
      "split": "random_seed123",
      "rep": "word",
      "key": "489b80bb2e39381283a7154f732a498915faadac8ff9deccb41e9d7c13f28ccd"
    },
    {
      "split": "random_seed123",
      "rep": "word_noanon",
      "key": "808b4d6cfea44a9cb762baa0cb2a0253fe54b4997b4acae444051b7b2228908a"
    },
    {
      "split": "random_seed123",
      "rep": "character_noanon",
      "key": "eab7deb98f54e8a449b1d4ff302f9a6fa6b312f780de82bb5e0e19d9fe14885c"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "word",
      "key": "d30ba234b19ccd80dfc77fa7a61cbad4f5888ec35b6064cd769b7b40c1568525"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "character",
      "key": "eb8c00b3ab4b70aad6cca4b300fed9d137e5fe147419b29893d0c597057f6f06"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "structural",
      "key": "9bc325ec85a745ddbe908f0c19ada488ac24c4f9bdad3a2c7339598f6e8b3200"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "word",
      "key": "d30ba234b19ccd80dfc77fa7a61cbad4f5888ec35b6064cd769b7b40c1568525"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "word_noanon",
      "key": "cbf636a3a91b9e0d1fcd5c0f0b68625dee0d502862b6776a6071a8a1668e6f5a"
    },
    {
      "split": "holdout_trec5_trec7",
      "rep": "character_noanon",
      "key": "fdadc83ba34d376e19182872298b886d7827c613b5fe5c5b19387d871e9c8663"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "word",
      "key": "1347750078cd63232340cb7488a035be08d998613201ebbc9b71d5988c72577e"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "character",
      "key": "c65bc9497c233fd308b6fd803fd77c65a8f89d6eb6d693cc9b5c7e2bc0bb5629"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "structural",
      "key": "a2ad01b239ff971685de735c61c659e5fdfd75855acc011e4c13cef5950bb892"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "word",
      "key": "1347750078cd63232340cb7488a035be08d998613201ebbc9b71d5988c72577e"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "word_noanon",
      "key": "da754031c33879d9908bcf9b668e2ebb3ecf74caa9d965976610a0d60d379130"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "rep": "character_noanon",
      "key": "306d461220b5b2868eb5dc19076bcfb193b82c6851c0a2f04a8a4125817bf964"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "word",
      "key": "4f95dfb32a8dc0c01e4a40b3f79819ac70c3e6a4438a81b159ff0ddd08867a5f"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "character",
      "key": "ef2bcb63055cf356d1f0016dcb655d18d0b0f56b31ad74380d0b4c6547ca2bce"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "structural",
      "key": "1dab6b560477b2f43e5c5ae44ec89f78405810d4544c4f359ddb62e3d008a286"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "word",
      "key": "4f95dfb32a8dc0c01e4a40b3f79819ac70c3e6a4438a81b159ff0ddd08867a5f"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "word_noanon",
      "key": "2a1980fb61c3ee01f18ae0975b24b3c8edb6a2a93885b350971980bf8643c4cf"
    },
    {
      "split": "holdout_trec6_trec7",
      "rep": "character_noanon",
      "key": "b0b9a33b92c3445beb84f7fedfdcdebe418ded3e3d3fb2b0b4de9e4834061cc0"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "word",
      "key": "c73b4fb358c50ff6a5a214175e0867a42651833dea430162a86b626a9537c6be"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "character",
      "key": "f644e1f30ad36b91ee3a504c245117d4205c2f36cb6ccd4a6738f114c81806dd"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "structural",
      "key": "8bc53835a0489c8e51a4c662c6f77e097ce68b8d8e703fc5d8d8a04ab2af4033"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "word",
      "key": "c73b4fb358c50ff6a5a214175e0867a42651833dea430162a86b626a9537c6be"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "word_noanon",
      "key": "bcf21cbcea4349e3bc2ea0970b3330dad8deeb25dabcd8c295fd7e5d5b7d7767"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "rep": "character_noanon",
      "key": "ba409170de96f54d2aed8ca92cd93db94990b15c325e1a1ae75864866ef0395e"
    },
    {
      "split": "holdout_trec7",
      "rep": "word",
      "key": "f2d99ae95020729e835585cb9195b62ea3bb27ba496fb8483f017218e5ee6c62"
    },
    {
      "split": "holdout_trec7",
      "rep": "character",
      "key": "69376e1c7d0fa575b8a15a18854ce8aa92e8bb5fc499d5f73c28fd900134a170"
    },
    {
      "split": "holdout_trec7",
      "rep": "structural",
      "key": "3b58dbda1aa263b6ccaa2c08dc8cd1087194493963d8b59d61377c1b0bbd4a64"
    },
    {
      "split": "holdout_trec7",
      "rep": "word",
      "key": "f2d99ae95020729e835585cb9195b62ea3bb27ba496fb8483f017218e5ee6c62"
    },
    {
      "split": "holdout_trec7",
      "rep": "word_noanon",
      "key": "0c37596cf030565a868840339d5ff50ece40035f1274d2ca4671d6b008009a11"
    },
    {
      "split": "holdout_trec7",
      "rep": "character_noanon",
      "key": "7a23b68c21a4f5b4cc05de08493ce52c450d5d0ece79ea0314285982355cee62"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "word",
      "key": "dd92a0b7b5589390b3d2044416cae4567750ea44a55af2b0a9d9015e78e758bc"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "character",
      "key": "21098b4c248e1a7a8ca284bb0961c6d44ec6e641ac9acd57f745f17b48e774d6"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "structural",
      "key": "ddbdb82141ee9dea18f57e6cf42fbff05bed52f24867967d4d392a10d8a4a475"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "word",
      "key": "dd92a0b7b5589390b3d2044416cae4567750ea44a55af2b0a9d9015e78e758bc"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "word_noanon",
      "key": "64b8d648fa3173b6c72e4fc8aab3f6df3eaef45f2dcf111aa0b35e38a08dae15"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "rep": "character_noanon",
      "key": "32860ca6a0ff691590282c9c5ad2dde6e8129688dd12ba52a520262719dc07ba"
    },
    {
      "split": "holdout_trec5",
      "rep": "word",
      "key": "a43fb3139809ff8f462291b4f2c8c97948680081a161b854a45f4249dd71232e"
    },
    {
      "split": "holdout_trec5",
      "rep": "character",
      "key": "1d16edfc48514529272b861ed4b8969e1b2303a3ea02c398327073d1b567ca4e"
    },
    {
      "split": "holdout_trec5",
      "rep": "structural",
      "key": "738145ee8d8b0719e8354eee5008652702383ad12f17847706e6ca0e05c8ee4d"
    },
    {
      "split": "holdout_trec5",
      "rep": "word",
      "key": "a43fb3139809ff8f462291b4f2c8c97948680081a161b854a45f4249dd71232e"
    },
    {
      "split": "holdout_trec5",
      "rep": "word_noanon",
      "key": "12ce39624dac4f3f6d5fd25797cd1c267e860b8daf8daeb1b7322aa0962a8db7"
    },
    {
      "split": "holdout_trec5",
      "rep": "character_noanon",
      "key": "759aedf5437d8158d9709d5bd4a0bb6eaeaee63b1ef1ed1f4a854ee1780da706"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "word",
      "key": "a669ca810dc6d444ec5b61e0db0c7d65a5eac7cfb1011b541977e532ebc41b1b"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "character",
      "key": "412645deeffd99763eeec0b31ffb86b2c3b3036b106847dbcd1b8a75bb2cb301"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "structural",
      "key": "849c051bf5751adc4701d8fe95b8ab287b7f7d1661cce21a73e00d3f06515567"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "word",
      "key": "a669ca810dc6d444ec5b61e0db0c7d65a5eac7cfb1011b541977e532ebc41b1b"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "word_noanon",
      "key": "58e08e873484cad09217dce2857a0ccc77e66989319dbc73db033da1000ba5d4"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "rep": "character_noanon",
      "key": "49eaf29a8eec5a1cc57edef59917601a26ea9d9660b81223c26df46c65d0490a"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "word",
      "key": "b86d829c1d882a41cf751d2ea71b1827cd2dfa5aea00cac508cace1a9822ddb8"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "character",
      "key": "98ff8678b64ea478f3090afc4abaa943d5d4f65d75979461bc5fb740d21fd4f2"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "structural",
      "key": "998bea8b0302bfb26edaa751ee38e8d67d1de0c9b502b84a826717fbc2757d87"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "word",
      "key": "b86d829c1d882a41cf751d2ea71b1827cd2dfa5aea00cac508cace1a9822ddb8"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "word_noanon",
      "key": "b5963db24aeaf0f3ed0eb640531ae43eca90ee3c03b002c3a15d81a75b24e6e2"
    },
    {
      "split": "holdout_trec5_trec6",
      "rep": "character_noanon",
      "key": "98d61af448820462993d6ddf62ef8dd8c7062334d10abc43e910c53b224ef961"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "word",
      "key": "61808d005821cdab3a7cc8ad679571aef79ec490c1bfe8e36b16b4bd2e1fe042"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "character",
      "key": "f1b67c66cd18b138f0ef768e0bdaa48457464938bf83ab2102102e9f8e3d6109"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "structural",
      "key": "1d8931936b9c9d21d415a8ddbcc575ff1e683101e4b6ee9007cbbc3d7b43cc79"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "word",
      "key": "61808d005821cdab3a7cc8ad679571aef79ec490c1bfe8e36b16b4bd2e1fe042"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "word_noanon",
      "key": "fe707c3f49d367f896f6a0fad70fe2447348f039142fd7652867b71a8237ede6"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "rep": "character_noanon",
      "key": "1f62c7bf5f2ad4d76048122fc68826d9b7ec9734e1b506a0411bb9a2dafa2467"
    },
    {
      "split": "holdout_trec6",
      "rep": "word",
      "key": "b56b5083703a8db41ca6279a58cad4e85b0cec7003ecdf7aa854ee4046c038d9"
    },
    {
      "split": "holdout_trec6",
      "rep": "character",
      "key": "c57aa9758c886acebbbdc0fffe847d865baf2b2a42f3539fe142f25669a51453"
    },
    {
      "split": "holdout_trec6",
      "rep": "structural",
      "key": "9fc186680eb317bf0a5733bbf9c94e0d2d3b88f2211444a7ac9b7ce7e37571d2"
    },
    {
      "split": "holdout_trec6",
      "rep": "word",
      "key": "b56b5083703a8db41ca6279a58cad4e85b0cec7003ecdf7aa854ee4046c038d9"
    },
    {
      "split": "holdout_trec6",
      "rep": "word_noanon",
      "key": "3688ea87fa1c7f6505721748dc73060705b7a7825f75ba11e5e0db5f939fa4bb"
    },
    {
      "split": "holdout_trec6",
      "rep": "character_noanon",
      "key": "62e3c908d490979055803065a55ec11fb4dcc202d43eb2e39fca32370bf97658"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "word",
      "key": "9b1004efbdaedeeac355e9b20b8a4caeafebed2b84b7e51873b0e721ca4d4e71"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "character",
      "key": "875cfc076a337167b9a365fb40e764ce2ca999506a13b8c1d539ece7befe1c6b"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "structural",
      "key": "3b8e52fcb59a392dbb2142f16885624fe6a726e08648d7f4ae87b95b262e5822"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "word",
      "key": "9b1004efbdaedeeac355e9b20b8a4caeafebed2b84b7e51873b0e721ca4d4e71"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "word_noanon",
      "key": "8e13ca5855cef99265d4d76003e77aec137f675915c481a85752233e7b3ccd8c"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "rep": "character_noanon",
      "key": "bfd9a487d85afb1c5e25027cc9c962796df5d9c86021c3af35b149072fe062fe"
    }
  ],
  "model_keys": [
    {
      "split": "random_seed42",
      "model": "word_logistic_regression",
      "key": "f01037474f1b93ab9f6cd91334aa8a4f53799434be4966cb054eed5ea3bff013"
    },
    {
      "split": "random_seed42",
      "model": "character_linear_svm",
      "key": "819c580db91274d54ab3834dd799208bd839db40b47a4b0f66edde7ad273f743"
    },
    {
      "split": "random_seed42",
      "model": "structural_logistic_regression",
      "key": "98e0dd8636ae5b557a0d77b6f61f817692b8d889ed68592a4baf24d5cad56046"
    },
    {
      "split": "random_seed42",
      "model": "word_xgboost",
      "key": "2d93b3f032f899bada70dc44e463dd1745a9de8d2a0da49d15fb0db0415d3c29"
    },
    {
      "split": "random_seed42",
      "model": "word_noanon_logistic_regression",
      "key": "b2039b7dcece69506f8bb6ad5b33e9116916ef557c5fec6d0bbe560444ef2a4d"
    },
    {
      "split": "random_seed42",
      "model": "character_noanon_linear_svm",
      "key": "750d9c890f0e262800c2733dfbcb48e8562746721935039b90862233426e0948"
    },
    {
      "split": "random_seed7",
      "model": "word_logistic_regression",
      "key": "1590cb3add0fbb36881318cf7b7df3d1b6e041d7fbe9a3f9a106ca3aec0d355e"
    },
    {
      "split": "random_seed7",
      "model": "character_linear_svm",
      "key": "42a26b132a626681088a54c69f3c2cf42ea3fb0571cd6b257b6118af8b0637a5"
    },
    {
      "split": "random_seed7",
      "model": "structural_logistic_regression",
      "key": "acf12bb9390af193b5dda1cc132d64442b0a8645f13adcf700b2797ce4e45957"
    },
    {
      "split": "random_seed7",
      "model": "word_xgboost",
      "key": "91c30382d98e829a5147ad9302389110c6436c7e617d19cc87965df124fc025d"
    },
    {
      "split": "random_seed7",
      "model": "word_noanon_logistic_regression",
      "key": "956532d2c1f1c53c859aa87b3b6f6f379b98ba2719b579a51270733df039f511"
    },
    {
      "split": "random_seed7",
      "model": "character_noanon_linear_svm",
      "key": "ddbe53efa666f40dd8f10ed7c3644c6738e47a76c90513158953c03fd452ff29"
    },
    {
      "split": "random_seed123",
      "model": "word_logistic_regression",
      "key": "e101cf1ba0e06857ba13c5f510a7a130b6a6d75cf33d34f168dd8a79dbad0891"
    },
    {
      "split": "random_seed123",
      "model": "character_linear_svm",
      "key": "970999453143a766dd0e6216647f9ef84726cd5a409ffbf54940757c7567128f"
    },
    {
      "split": "random_seed123",
      "model": "structural_logistic_regression",
      "key": "97bf820a64b98c31699075f4ba2320bd3bf33b68016ab732c222032e58709546"
    },
    {
      "split": "random_seed123",
      "model": "word_xgboost",
      "key": "66d0fab43efeb11882109ab9add087c2e08cc1736cc7bce97bdb087128b9eb62"
    },
    {
      "split": "random_seed123",
      "model": "word_noanon_logistic_regression",
      "key": "c7d5186fba72ce7640adfeeabb0752647e71e714ea40dffaa2869a4839d5f788"
    },
    {
      "split": "random_seed123",
      "model": "character_noanon_linear_svm",
      "key": "ad8c6619038ad22a4160568bdfff23ada7f7c5463dcd1ff1213496b6cda6c018"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "word_logistic_regression",
      "key": "3749fee8b75d5d30873183502fe33c47a72c947394a44e04f35f280c924bb2be"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "character_linear_svm",
      "key": "eb419de03b3d7df3ac7bee34d0b516d399e727146fd6137e57f32e470287d063"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "structural_logistic_regression",
      "key": "3c25b9e91aef1af2d392ada4c715f7fd9fd98a8616d95266e695856665391cc4"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "word_xgboost",
      "key": "d8423359f054ee3812733d4d2cf641baa96a2419e090eedeeb883fc1d7dfa4cc"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "ebe52f74b9a5c0d607f0d1852420dcdd5662e1277b6c33b82b6753a2c0e873a3"
    },
    {
      "split": "holdout_trec5_trec7",
      "model": "character_noanon_linear_svm",
      "key": "683a2c8388e0bf81f4ad2f8a1136d4ef5e029935fbcc626aff83fb8ab030def0"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "word_logistic_regression",
      "key": "534827e997264f49f04a8d088af9eddf8469152f5fdc9522213d197ef7b03e0a"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "character_linear_svm",
      "key": "8183abc12529218c4563011bb726a11b7235bff133fbc44b333f62af366e8025"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "structural_logistic_regression",
      "key": "e912956f4022a3929c11fa7f23f076055cf5446faa4211b3e12d2d81ce041dab"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "word_xgboost",
      "key": "273d562480d4a25c83e16b4e82b1bc6a8b996bcaab323cb48e66a48d8bcd5ae7"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "af78116311a1493a8f30e97941daea6f5953d55725b81b073ca013b198f9d7ff"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec7",
      "model": "character_noanon_linear_svm",
      "key": "67417a70fa49c7448f0a663029253969a005420a15a3141476d6ff8f2a8cca0c"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "word_logistic_regression",
      "key": "e7f1973006baa859600d4b64c317889c2d8bc1e08640f7a3a75b2f2566559e63"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "character_linear_svm",
      "key": "b5d1d7777de924652ae83b6f87bf696fe42110bddc71f17a78d9d346467238fc"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "structural_logistic_regression",
      "key": "70f38cf7e5b851e9785a47c5b1ba1a0928c8aa7df37b2445b035ad6207908eb1"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "word_xgboost",
      "key": "82f081e64a9ec715236c22da4b83cfb680138b08d25297e2bff808c923503387"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "ddb9cd8d8da66a7ff0fa97345080390e4aba867feb3ddd24311ac7e3feb8728c"
    },
    {
      "split": "holdout_trec6_trec7",
      "model": "character_noanon_linear_svm",
      "key": "4631130c2dbadba8274c391d1da150f22d5540b9c8c2737736810565335beb58"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "word_logistic_regression",
      "key": "e755e182685f62c326602efb03dca5ef7fa7e2b58572d35120051eb8db5d8a2a"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "character_linear_svm",
      "key": "0e2ade801412ddb0b92ba117203ea4a4bb047e1131e5e5c1d54e09fdd7fd6c64"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "structural_logistic_regression",
      "key": "bc56d1b14968027d1a05a2737dd0959f91be80a82066c63e405908df75b6fbd5"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "word_xgboost",
      "key": "503c88c409b59eaad187c93d3b253ac77a0498752a9828fd30291df53c711693"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "f53b3b9fff69d9a44105296f8a6eba599e1e491f8c95366f0adcc8e4e9af25a9"
    },
    {
      "split": "random_seed42_eq_holdout_trec6_trec7",
      "model": "character_noanon_linear_svm",
      "key": "7c02728ed70f1670b0f734b6073d8948e8b55bb5fa58c625efb6793fb3e9c8fb"
    },
    {
      "split": "holdout_trec7",
      "model": "word_logistic_regression",
      "key": "bee14a56c25dee01b3488ff8f26fd3437317e164a0a8371e129908af9598af9c"
    },
    {
      "split": "holdout_trec7",
      "model": "character_linear_svm",
      "key": "c28d75adbfd0b34ed283d6652f33cea89bb420fe7972529ca2cef4ae122b41c7"
    },
    {
      "split": "holdout_trec7",
      "model": "structural_logistic_regression",
      "key": "c174f1fb8f7673e40618c0b2cd1e9d98ebddbe9cb77f8de3210c832d5228c57c"
    },
    {
      "split": "holdout_trec7",
      "model": "word_xgboost",
      "key": "80b45d7e3932ccb01d62178915db5fb47c62f1d808fa32f701b33bf7bd92b814"
    },
    {
      "split": "holdout_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "aca1cc671881af9b493babcb602998354ceb0541e4ea9a032ad7c8c16da96efb"
    },
    {
      "split": "holdout_trec7",
      "model": "character_noanon_linear_svm",
      "key": "2353470c50dd116449cf186c6a660b8fae3f5cc3eb92cbb9d9640cf078f2823b"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "word_logistic_regression",
      "key": "d80b97e0da3a9297da32db31d079e916593c4cfc3de5b5b1e0fabcc6e5dcb772"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "character_linear_svm",
      "key": "8932954d3627c040d4cd8579e25ca481333d159da23a1ad3a33a7eff2d4e505f"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "structural_logistic_regression",
      "key": "29d7307c67474b7fd5ccab97e3f07a0a200616c3fd68cbbbd0ca28eaccd567b0"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "word_xgboost",
      "key": "f7d1fe74b120d82799dfa02833a9aeab865d034ec5a9ff965c5cd8eb3351371f"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "word_noanon_logistic_regression",
      "key": "fb1d81b13cc6831c67fdb7bf26914109b932ed458dae0fff9734a017819af792"
    },
    {
      "split": "random_seed42_eq_holdout_trec7",
      "model": "character_noanon_linear_svm",
      "key": "98180e9611253ebdc9712b6b2cd8d4b7f49e4f504ad8489b74b3f10b42c56a7f"
    },
    {
      "split": "holdout_trec5",
      "model": "word_logistic_regression",
      "key": "03d3878afd73e4384f552a7a69be943ab931cb8c1df8b9a1a0523f701ff651ae"
    },
    {
      "split": "holdout_trec5",
      "model": "character_linear_svm",
      "key": "bed33934e3f71a78fe2f26e9b07e35f5340903245a4442b11c08a2f74b850044"
    },
    {
      "split": "holdout_trec5",
      "model": "structural_logistic_regression",
      "key": "4d51b06204ad58573f103a11266902f499fe4b501af102883bd5bf01ae725dc7"
    },
    {
      "split": "holdout_trec5",
      "model": "word_xgboost",
      "key": "06ab3a9a81ad67c00e296fd0cea4f9a2c573bdc918f989e9a52728bd3b74db31"
    },
    {
      "split": "holdout_trec5",
      "model": "word_noanon_logistic_regression",
      "key": "488e2f46d59b48e545994a529c07ab11428ed49f90ff2f82cea5758dd45456aa"
    },
    {
      "split": "holdout_trec5",
      "model": "character_noanon_linear_svm",
      "key": "58f0fe91aa309a2b10c9864bcdf1bb073e99386292b432e6b3eca9a43f9f2120"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "word_logistic_regression",
      "key": "f1061f686d0acf037bba72734f8eda0dc28dd0ce0c35dc328bd8fc3f6ca86b07"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "character_linear_svm",
      "key": "ab3b837dc43fd084936883b4a1c4e097550020fa50b7ca573e2f16845641d02b"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "structural_logistic_regression",
      "key": "31207c4c0ae21e3710c4b4d754bf5a4a882e96547526feb19096e7210209a0a6"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "word_xgboost",
      "key": "1c056d1191e7ab02cda7009ae06169ede98170bbf61afd9b0e0e4624c12c66a1"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "word_noanon_logistic_regression",
      "key": "deed685de613e465f9777a12209b095d1973c4c5f24ae6cfae1d396390c7b72c"
    },
    {
      "split": "random_seed42_eq_holdout_trec5",
      "model": "character_noanon_linear_svm",
      "key": "fc94ac72cb3566ba0b1ca695253f9c7c964b58be0acceb2d778ed892203c70d8"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "word_logistic_regression",
      "key": "d2b229084c717c1085e6dde2831705f121a5461885dd615fa03bcbd3e0832979"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "character_linear_svm",
      "key": "05c907891ea650b4e573d377884586adc57028d3a2d0a150125744202f2f9f30"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "structural_logistic_regression",
      "key": "787715a80fc020b6c81805258f3fffd1e4b1701ab503318b779c160babf97bd1"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "word_xgboost",
      "key": "4d46cd4861ba0fcd81e5b59ce7f09ea599f577f3dc91940ce6e9b490fb7c9355"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "word_noanon_logistic_regression",
      "key": "bb2f4eac3f1bb6fbf48da8de3b269f9ca3e1cbe109e494d95041455a4ffcdfc2"
    },
    {
      "split": "holdout_trec5_trec6",
      "model": "character_noanon_linear_svm",
      "key": "8ce4d9cc28cca3e60a3368a379b6929b7e27b9b69086855cf012043cbe4ac100"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "word_logistic_regression",
      "key": "e3a1ad1488c30e23aa066ae91541a211d984429278f9b650b5c529c716651c5f"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "character_linear_svm",
      "key": "2da8cea109bd5a5f3143370fa2528836ec78edb833c18fe3a26cca12b07e29d8"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "structural_logistic_regression",
      "key": "5ec85a4b8773e554e054b2f83a545c9a14aaf8687aa512ed64b1667ed484430e"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "word_xgboost",
      "key": "173c7c41d2c775ca1fb9559b226b718c6324688acecfc00582fa67977e7525ce"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "word_noanon_logistic_regression",
      "key": "7198d278a8fa77d61dabaeb1c5d5bd76362c4ab33b4bcd9433665a9dd31fd74d"
    },
    {
      "split": "random_seed42_eq_holdout_trec5_trec6",
      "model": "character_noanon_linear_svm",
      "key": "da57ff5a9297e6f7f1fb449ff7b191ed0e692eb36f4d7706162ae934f8a69781"
    },
    {
      "split": "holdout_trec6",
      "model": "word_logistic_regression",
      "key": "bd0eed63d62f46523d5297cbd2c5d5695efa33ec21186c11c08fce1217a74372"
    },
    {
      "split": "holdout_trec6",
      "model": "character_linear_svm",
      "key": "49f05910e31e7af5810ebd22fa0ce4233e2d05385bc011cda9d0a317cd729bc3"
    },
    {
      "split": "holdout_trec6",
      "model": "structural_logistic_regression",
      "key": "106328dd967fcb4853e17c7d2473292bd620de051b20d4795dc3f083f2a930bf"
    },
    {
      "split": "holdout_trec6",
      "model": "word_xgboost",
      "key": "fb3848cc9f44f595b3c6ab7029a3b1eb18354d0f29ed1e69c744101ecffd5153"
    },
    {
      "split": "holdout_trec6",
      "model": "word_noanon_logistic_regression",
      "key": "155a9a2e412563b5eabfcbfd9c72da7f81c1901d47e697f74cafcd2958d66561"
    },
    {
      "split": "holdout_trec6",
      "model": "character_noanon_linear_svm",
      "key": "e19f51af84e8e5f7b3e138294cd55fcb23c533ae71aaba1f6a07f83213bc3553"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "word_logistic_regression",
      "key": "48d1874961d8de06dcfdd3d21a226819c77fc7d1c94ae9ebf371f7bdb95dcf70"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "character_linear_svm",
      "key": "09becdd896e3af6c647337906fc05a042a8ff896690371576cfacafcbd0d6963"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "structural_logistic_regression",
      "key": "369e55df23a54471440906e5fea3dcb60897e21d2cb1ce1c8441a086d4243eb6"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "word_xgboost",
      "key": "81cc6dc2a38ed62006760f02796de5cbca504be9a43c492c1575b3a20e549954"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "word_noanon_logistic_regression",
      "key": "2ef0bf23806f5fa6934981576f4300f3e9e9cdec73744b4076891f1c26a5a4c1"
    },
    {
      "split": "random_seed42_eq_holdout_trec6",
      "model": "character_noanon_linear_svm",
      "key": "c58ec9eed13544375eedd1f23032858140cdb193e5f583096f52d7ec93b341ba"
    }
  ],
  "prediction_files": [
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed123.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec5_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec6_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec7.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec5.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec5_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_logistic_regression__random_seed42_eq_holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_linear_svm__random_seed42_eq_holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\structural_logistic_regression__random_seed42_eq_holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_xgboost__random_seed42_eq_holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\word_noanon_logistic_regression__random_seed42_eq_holdout_trec6.parquet",
    "D:\\Aston\\DeceptionEmail\\outputs\\runs\\20260811T162016Z_d2881b85\\predictions\\character_noanon_linear_svm__random_seed42_eq_holdout_trec6.parquet"
  ],
  "timings": {
    "word_logistic_regression__random_seed42": {
      "fit_time_s": 2.659913299998152,
      "inference_time_s_median": 0.03188609999779146,
      "peak_mem_gb": 0.21
    },
    "character_linear_svm__random_seed42": {
      "fit_time_s": 4.688981200000853,
      "inference_time_s_median": 0.26335459999972954,
      "peak_mem_gb": 1.38
    },
    "structural_logistic_regression__random_seed42": {
      "fit_time_s": 0.6763884000101825,
      "inference_time_s_median": 0.003004099999088794,
      "peak_mem_gb": 0.02
    },
    "word_xgboost__random_seed42": {
      "fit_time_s": 141.46850540000014,
      "inference_time_s_median": 0.4288594999961788,
      "peak_mem_gb": 1.92
    },
    "word_noanon_logistic_regression__random_seed42": {
      "fit_time_s": 2.7774667000048794,
      "inference_time_s_median": 0.03264109999872744,
      "peak_mem_gb": 0.19
    },
    "character_noanon_linear_svm__random_seed42": {
      "fit_time_s": 4.806313900000532,
      "inference_time_s_median": 0.24948009999934584,
      "peak_mem_gb": 1.26
    },
    "word_logistic_regression__random_seed7": {
      "fit_time_s": 2.7167457999894395,
      "inference_time_s_median": 0.03630749999138061,
      "peak_mem_gb": 0.2
    },
    "character_linear_svm__random_seed7": {
      "fit_time_s": 4.708685500008869,
      "inference_time_s_median": 0.27410389999567997,
      "peak_mem_gb": 1.37
    },
    "structural_logistic_regression__random_seed7": {
      "fit_time_s": 0.6049500000081025,
      "inference_time_s_median": 0.0037930000107735395,
      "peak_mem_gb": 0.02
    },
    "word_xgboost__random_seed7": {
      "fit_time_s": 142.2715281000128,
      "inference_time_s_median": 0.383062399996561,
      "peak_mem_gb": 1.78
    },
    "word_noanon_logistic_regression__random_seed7": {
      "fit_time_s": 2.96029859999544,
      "inference_time_s_median": 0.03576969999994617,
      "peak_mem_gb": 0.19
    },
    "character_noanon_linear_svm__random_seed7": {
      "fit_time_s": 4.5312132999970345,
      "inference_time_s_median": 0.2261642999947071,
      "peak_mem_gb": 1.26
    },
    "word_logistic_regression__random_seed123": {
      "fit_time_s": 2.7241585000010673,
      "inference_time_s_median": 0.037631200000760145,
      "peak_mem_gb": 0.2
    },
    "character_linear_svm__random_seed123": {
      "fit_time_s": 4.640553099990939,
      "inference_time_s_median": 0.26820230000885203,
      "peak_mem_gb": 1.38
    },
    "structural_logistic_regression__random_seed123": {
      "fit_time_s": 0.839207000011811,
      "inference_time_s_median": 0.005208100003073923,
      "peak_mem_gb": 0.02
    },
    "word_xgboost__random_seed123": {
      "fit_time_s": 142.5060247999936,
      "inference_time_s_median": 0.41667730000335723,
      "peak_mem_gb": 2.08
    },
    "word_noanon_logistic_regression__random_seed123": {
      "fit_time_s": 2.8342142999899806,
      "inference_time_s_median": 0.039542600003187545,
      "peak_mem_gb": 0.19
    },
    "character_noanon_linear_svm__random_seed123": {
      "fit_time_s": 4.179646899996442,
      "inference_time_s_median": 0.24495310000202153,
      "peak_mem_gb": 1.26
    },
    "word_logistic_regression__holdout_trec5_trec7": {
      "fit_time_s": 0.41500839999935124,
      "inference_time_s_median": 0.13382439999259077,
      "peak_mem_gb": 0.04
    },
    "character_linear_svm__holdout_trec5_trec7": {
      "fit_time_s": 1.0473019000055501,
      "inference_time_s_median": 1.179829200002132,
      "peak_mem_gb": 0.25
    },
    "structural_logistic_regression__holdout_trec5_trec7": {
      "fit_time_s": 0.04984360000526067,
      "inference_time_s_median": 0.020926700002746657,
      "peak_mem_gb": 0.0
    },
    "word_xgboost__holdout_trec5_trec7": {
      "fit_time_s": 35.99877720000222,
      "inference_time_s_median": 2.1907256999984384,
      "peak_mem_gb": 0.29
    },
    "word_noanon_logistic_regression__holdout_trec5_trec7": {
      "fit_time_s": 0.4055518000095617,
      "inference_time_s_median": 0.1155704999982845,
      "peak_mem_gb": 0.04
    },
    "character_noanon_linear_svm__holdout_trec5_trec7": {
      "fit_time_s": 0.9698138999956427,
      "inference_time_s_median": 1.0496687999984715,
      "peak_mem_gb": 0.23
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 0.5278240999905393,
      "inference_time_s_median": 0.17681429999356624,
      "peak_mem_gb": 0.03
    },
    "character_linear_svm__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 0.9550645999988774,
      "inference_time_s_median": 1.1571654999861494,
      "peak_mem_gb": 0.24
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 0.035112400000798516,
      "inference_time_s_median": 0.015570200004731305,
      "peak_mem_gb": 0.0
    },
    "word_xgboost__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 36.674795700004324,
      "inference_time_s_median": 2.4301439999981085,
      "peak_mem_gb": 0.3
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 0.3871445999975549,
      "inference_time_s_median": 0.1746899999998277,
      "peak_mem_gb": 0.03
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec5_trec7": {
      "fit_time_s": 0.9074481999996351,
      "inference_time_s_median": 1.0607541000063065,
      "peak_mem_gb": 0.22
    },
    "word_logistic_regression__holdout_trec6_trec7": {
      "fit_time_s": 1.3313209999905666,
      "inference_time_s_median": 0.0854807999858167,
      "peak_mem_gb": 0.11
    },
    "character_linear_svm__holdout_trec6_trec7": {
      "fit_time_s": 2.3461489000037545,
      "inference_time_s_median": 0.6912494999996852,
      "peak_mem_gb": 0.7
    },
    "structural_logistic_regression__holdout_trec6_trec7": {
      "fit_time_s": 0.1235372999944957,
      "inference_time_s_median": 0.01078620000043884,
      "peak_mem_gb": 0.0
    },
    "word_xgboost__holdout_trec6_trec7": {
      "fit_time_s": 74.64050399999542,
      "inference_time_s_median": 1.5473754000122426,
      "peak_mem_gb": 1.39
    },
    "word_noanon_logistic_regression__holdout_trec6_trec7": {
      "fit_time_s": 1.286545800001477,
      "inference_time_s_median": 0.08106680000491906,
      "peak_mem_gb": 0.1
    },
    "character_noanon_linear_svm__holdout_trec6_trec7": {
      "fit_time_s": 2.4010627000097884,
      "inference_time_s_median": 0.7543731999903684,
      "peak_mem_gb": 0.64
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 1.6484819000033895,
      "inference_time_s_median": 0.10356490001140628,
      "peak_mem_gb": 0.11
    },
    "character_linear_svm__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 3.1843935999932,
      "inference_time_s_median": 0.6915763000142761,
      "peak_mem_gb": 0.77
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 0.1757382000068901,
      "inference_time_s_median": 0.015231999990646727,
      "peak_mem_gb": 0.0
    },
    "word_xgboost__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 85.52268580000964,
      "inference_time_s_median": 1.270576599999913,
      "peak_mem_gb": 1.37
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 1.583717900008196,
      "inference_time_s_median": 0.10783379999338649,
      "peak_mem_gb": 0.11
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec6_trec7": {
      "fit_time_s": 2.643652700004168,
      "inference_time_s_median": 0.6119599999947241,
      "peak_mem_gb": 0.71
    },
    "word_logistic_regression__holdout_trec7": {
      "fit_time_s": 2.0016924000083236,
      "inference_time_s_median": 0.07465490000322461,
      "peak_mem_gb": 0.14
    },
    "character_linear_svm__holdout_trec7": {
      "fit_time_s": 3.206914599999436,
      "inference_time_s_median": 0.528274500000407,
      "peak_mem_gb": 0.94
    },
    "structural_logistic_regression__holdout_trec7": {
      "fit_time_s": 0.26440279999224003,
      "inference_time_s_median": 0.007896600000094622,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__holdout_trec7": {
      "fit_time_s": 99.60268840000208,
      "inference_time_s_median": 0.9799772999976994,
      "peak_mem_gb": 1.26
    },
    "word_noanon_logistic_regression__holdout_trec7": {
      "fit_time_s": 1.82285649998812,
      "inference_time_s_median": 0.06663090000802185,
      "peak_mem_gb": 0.14
    },
    "character_noanon_linear_svm__holdout_trec7": {
      "fit_time_s": 3.1286395999923116,
      "inference_time_s_median": 0.5153673000022536,
      "peak_mem_gb": 0.86
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 1.9522970999969402,
      "inference_time_s_median": 0.08022489999711979,
      "peak_mem_gb": 0.15
    },
    "character_linear_svm__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 3.3610022000066238,
      "inference_time_s_median": 0.5316658999945503,
      "peak_mem_gb": 1.01
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 0.7568824000045424,
      "inference_time_s_median": 0.007985500007634982,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 111.29667280000285,
      "inference_time_s_median": 1.1341152999957558,
      "peak_mem_gb": 1.7
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 2.087389099993743,
      "inference_time_s_median": 0.06798279999929946,
      "peak_mem_gb": 0.14
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec7": {
      "fit_time_s": 3.250562400004128,
      "inference_time_s_median": 0.4610382999962894,
      "peak_mem_gb": 0.93
    },
    "word_logistic_regression__holdout_trec5": {
      "fit_time_s": 1.8621914999966975,
      "inference_time_s_median": 0.06402040000830311,
      "peak_mem_gb": 0.15
    },
    "character_linear_svm__holdout_trec5": {
      "fit_time_s": 3.2741970000060974,
      "inference_time_s_median": 0.5416296000039438,
      "peak_mem_gb": 1.03
    },
    "structural_logistic_regression__holdout_trec5": {
      "fit_time_s": 0.7659777000080794,
      "inference_time_s_median": 0.012307400000281632,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__holdout_trec5": {
      "fit_time_s": 114.27797340000689,
      "inference_time_s_median": 1.426139500006684,
      "peak_mem_gb": 1.7
    },
    "word_noanon_logistic_regression__holdout_trec5": {
      "fit_time_s": 1.8386086999962572,
      "inference_time_s_median": 0.05204589999630116,
      "peak_mem_gb": 0.14
    },
    "character_noanon_linear_svm__holdout_trec5": {
      "fit_time_s": 2.8743981000006897,
      "inference_time_s_median": 0.484003900011885,
      "peak_mem_gb": 0.95
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 1.8630059999995865,
      "inference_time_s_median": 0.07930090000445489,
      "peak_mem_gb": 0.14
    },
    "character_linear_svm__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 3.482227700005751,
      "inference_time_s_median": 0.5502445000020089,
      "peak_mem_gb": 0.95
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 0.273652600008063,
      "inference_time_s_median": 0.013030400004936382,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 111.9279133999953,
      "inference_time_s_median": 1.3162520000041695,
      "peak_mem_gb": 1.61
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 1.8761152000079164,
      "inference_time_s_median": 0.08455149999645073,
      "peak_mem_gb": 0.13
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec5": {
      "fit_time_s": 3.2748472999955993,
      "inference_time_s_median": 0.5413575999991735,
      "peak_mem_gb": 0.88
    },
    "word_logistic_regression__holdout_trec5_trec6": {
      "fit_time_s": 1.4076826999953482,
      "inference_time_s_median": 0.08399769999959972,
      "peak_mem_gb": 0.12
    },
    "character_linear_svm__holdout_trec5_trec6": {
      "fit_time_s": 2.349127099994803,
      "inference_time_s_median": 0.7093463000055635,
      "peak_mem_gb": 0.79
    },
    "structural_logistic_regression__holdout_trec5_trec6": {
      "fit_time_s": 0.5510607000032905,
      "inference_time_s_median": 0.013245900001493283,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__holdout_trec5_trec6": {
      "fit_time_s": 80.42993969999952,
      "inference_time_s_median": 1.6487972000031732,
      "peak_mem_gb": 1.43
    },
    "word_noanon_logistic_regression__holdout_trec5_trec6": {
      "fit_time_s": 1.31500080000842,
      "inference_time_s_median": 0.07642440000199713,
      "peak_mem_gb": 0.11
    },
    "character_noanon_linear_svm__holdout_trec5_trec6": {
      "fit_time_s": 2.2658437000063714,
      "inference_time_s_median": 0.5945168000034755,
      "peak_mem_gb": 0.73
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 1.2957844999909867,
      "inference_time_s_median": 0.1088815999974031,
      "peak_mem_gb": 0.1
    },
    "character_linear_svm__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 2.7510703000007197,
      "inference_time_s_median": 0.7923776999959955,
      "peak_mem_gb": 0.71
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 0.2883311000041431,
      "inference_time_s_median": 0.010855599990463816,
      "peak_mem_gb": 0.01
    },
    "word_xgboost__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 87.94721470000513,
      "inference_time_s_median": 1.783748400004697,
      "peak_mem_gb": 1.2
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 1.562875499992515,
      "inference_time_s_median": 0.17319169999973383,
      "peak_mem_gb": 0.1
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec5_trec6": {
      "fit_time_s": 2.4880211999989115,
      "inference_time_s_median": 0.7236145000060787,
      "peak_mem_gb": 0.65
    },
    "word_logistic_regression__holdout_trec6": {
      "fit_time_s": 3.3538723999954527,
      "inference_time_s_median": 0.02186690000235103,
      "peak_mem_gb": 0.22
    },
    "character_linear_svm__holdout_trec6": {
      "fit_time_s": 4.829003799997736,
      "inference_time_s_median": 0.18215860000054818,
      "peak_mem_gb": 1.48
    },
    "structural_logistic_regression__holdout_trec6": {
      "fit_time_s": 5.900270799989812,
      "inference_time_s_median": 0.0026415000029373914,
      "peak_mem_gb": 0.02
    },
    "word_xgboost__holdout_trec6": {
      "fit_time_s": 151.89228379999986,
      "inference_time_s_median": 0.4565632000012556,
      "peak_mem_gb": 1.76
    },
    "word_noanon_logistic_regression__holdout_trec6": {
      "fit_time_s": 2.933426800009329,
      "inference_time_s_median": 0.03351989999646321,
      "peak_mem_gb": 0.21
    },
    "character_noanon_linear_svm__holdout_trec6": {
      "fit_time_s": 4.480634599996847,
      "inference_time_s_median": 0.15609559998847544,
      "peak_mem_gb": 1.36
    },
    "word_logistic_regression__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 3.2636748000077205,
      "inference_time_s_median": 0.03355269999883603,
      "peak_mem_gb": 0.21
    },
    "character_linear_svm__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 5.174974599998677,
      "inference_time_s_median": 0.16096490000199992,
      "peak_mem_gb": 1.48
    },
    "structural_logistic_regression__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 1.2096248000016203,
      "inference_time_s_median": 0.003353200008859858,
      "peak_mem_gb": 0.02
    },
    "word_xgboost__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 162.62333180000132,
      "inference_time_s_median": 0.49816329999885056,
      "peak_mem_gb": 2.24
    },
    "word_noanon_logistic_regression__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 3.0922082999895792,
      "inference_time_s_median": 0.027325700008077547,
      "peak_mem_gb": 0.2
    },
    "character_noanon_linear_svm__random_seed42_eq_holdout_trec6": {
      "fit_time_s": 4.727552900003502,
      "inference_time_s_median": 0.1494576999975834,
      "peak_mem_gb": 1.36
    }
  },
  "peak_mem_gb": 2.24,
  "seed": 42
}
  ```
