# EnGENE

EnGENE is an AI powered Genetic Enhancement Engine for biologists and data scientists.

### A brief biology background

Genetics is an area of biology that studies DNA and genomics. A DNA is (in real life) two string of data that describes an organism. While it's imaginable that the DNA of a human and a grain of rice is different, the examples given here are specific to a single organism... so let's focus on humans!

As humans, we have our differences, even though we share the same DNA structure. So what makes us different? The answer is simple: DNA. It sounds quite complicated, but let me clear things our for you: 99% of our DNA is what makes us human, the other 1% is what makes us... us. That 1% DNA data is what we call **Single Nucleotide Polymorphisms (SNPs)**.

SNPs are basically a piece of DNA that is interchangeable throughout the species. Those dictate our appearance, bodily processes, tendency to diseases, etc..

In Genetic Enhancement, the main goal of the researchers is to find the SNPs that are related to a certain target characteristic of a organism. As another example, let's say that we want to make a certain crop grow faster. We first have to look at it's SNP string and figure out what SNPs are related to the "grow faster" characteristic. After that, researchers perform experiments to get a genotype that has that SNP set to a value that makes the "grow faster" characteristic bigger. The problem is that organisms can have thousands and thousands of SNPS. Some easily get to the millions. How do we find one SNP that is related to our target characteristic? That's what EnGENE is for! 

### The Engine

EnGENE is a model-based processor. It creates models out of .csv files and provides functions to manipulate and calculate SNP importance.

Every model created by EnGENE trains a determined number of Random Forest classifiers that find the optimal SNPs related to the target characteristic. EnGENE provides multicore processing for faster training of the models.

# Documentation

## Model Class
The model class is the main class in EnGENE. It's used to store SNP data, process and present it.

| Atribute | Type  | Description |
|--|--|--|
| modelname | String | the name used to reference the model |
| filename | String| the path to the referenced .csv file |
| data | pandas DataFrame | the DataFrame that stores all data from the .csv file
| target_column| String | the name of the column in data that is related to the target characteristic
| target_index | Int | the index of the target_column
| feature_range | list | stores the index to the first and last SNP columns
| X_train | pandas DataFrame | a subset of data that encapsules only the feature space.
| y_train | pandas DataFrame | a subset of data that encapsules only the target column. It's a complement to the X_train
| X_test| pandas.DataFrame | the remaining subset of data's feature space
| y_test| pandas.DataFrame | the remaining subset of data's target column
| classifier | sklearn.ensemble.RandomForestClassifier| the AI module that will be trained
| precision | float | the precision metric of the classifier|
| recall| float | the recall metric of the classifier|
| importance | dictionary | a dictionary that uses SNPs as keys and their importance score as values
| times_fit | int | the number of times the model was trained
|top_snps | list | an list of SNPs ordered by their importance to a characteristic

**Model([String]name, [String]filename)**: Creates a new model. Name can be anything you'd like. It's recommended to use a easy to associate name. Filename is the path to the .csv file that is related to the SNP information.
**Model.calculate_top_snps():** Calculates the best ranked SNPs in a fitted model.

**Model.create_dummies()**: Binarifies all columns in feature space inplace.
Lets's suppose the feature space is from column 1 to 3
| ID | SNP1 | SNP2 | SNP3 | Result |
|--|--| --| --| --|
| 1 | A | C | T | class_1 |
| 2 | G | T | A | class_2 |
| 3 | A | T | T | class_3 |

It will become:

| ID | SNP1_A | SNP1_G | SNP2_C | SNP2_T | SNP3_T | SNP3_A | Result |
|--|--| --| --| --| --|--|--|
| 1 | 1 | 0 | 1 | 0 | 1 | 0 | class_1
| 2 | 0 | 1 | 0 | 1 | 0 | 1 | class_2
| 3 | 1 | 0 | 0 | 1 | 1 | 0 | class_3

**Model.cross_check_models([Model or list of Models]model):** Crosses SNP data from similarly trained models gets a cross reference of important SNPs. Returns a list of SNPs sorted by importance.

**Model.destroy_column([int or list of ints] column):** Drops column(s) from Model.data inplace. Returns a list of dropped column names.

**Model.fit([int] cpu=-1):** Trains the classifier using X_train and y_train. Cpu is the amount of cores used to process the training.

**Model.get_classes():** Returns a list of all distinct values in target column.

**Model.get_mean_precision():** Returns the mean precision metric of all training runs.

 **Model.get_mean_recall():** Returns the mean recall metric of all training runs.

**Model.get_top_snps([int] top=10):** Returns a list with the topn most important SNPs in model.

**Model.holdout([float] train_s=0.9, [bool] stratify=True):** Applies the holdout operation to data, creating X_train, y_train, X_test and y_test in place. Every holdout if random and unique.

**Model.massfit([int] n, [float] train_s=0.9, [bool] stratify=True):** Applies holdout() with train_s and stratify and fit() n times.

**Model.one_vs_all_transform([string] target_class):** Applies the one_vs_all problem transformation to data inplace.

Before:
| ID | SNP1 | SNP2 | SNP3 | Result |
|--|--| --| --| --|
| 1 | A | C | T | class_1 |
| 2 | G | T | A | class_2 |
| 3 | A | T | T | class_3 |

After running Model.one_vs_all_transform("class_2"):
| ID | SNP1 | SNP2 | SNP3 | Result |
|--|--| --| --| --|
| 1 | A | C | T | Other |
| 2 | G | T | A | class_2 |
| 3 | A | T | T | Other |

**Model.print_non_features():** Returns a list of all column names and indexes outside feature_range.

**Model.save_to_csv():** Saves Model.data to a new .csv file in Saved_Models folder.

**Model.set_feature_range([int] start, [int] end):** Sets the range of column indexes that the model will understand as the feature space.

**Model.set_target_column([int or string] indicator):** Sets the target column of the model by name or index.

**Model.unload():** Frees all SNP data from Model, making it read-only.

**Model.__calculate_cross_check_multiplier():** Applies gain multiplier to all scores in a Model crossing operation.

**Model.__format_string([string] text):** Returns a version of text that has left padding of 20 spaces.

**Model.__reindex([int] n, [list] l=[]):** Auto-fix feature_range after deletion in Model.destroy_column.

## Credits

EnGENE was developed by Henrique Frajacomo, researcher in BioMaL lab based at Federal University of São Carlos - Brazil.