# EnGENE-Terminal Tutorial

To get started with EnGENE analysis, all you need to learn is three special commands: *Load, Train and Snp*.

## Load

Description: Loads and prepares a model based on input dataset and user-given information
Syntax: `Load <name> <filename> <feature_space_start> <feature_space_end> <target_column> <target_class>? &`

*Name*: The name to be given to the new model
*Filename*: Path to input dataset
*Feature_space_start*: An integer that represents the column index of the first SNP. Starts at 0.
*Feature_space_end*: An integer that represents the column index of the last SNP. Starts at 0.
*Target_column*: The column name or integer representing the column index of the investigated feature
*Target_class*: The specific value of the target column that wants to be discovered (ignore if there are only two classes)

Example 1: `Load test_model models/test.csv 1 10 growth_speed fast &`
Example 2: `Load model_a rice.csv 1 4000 amylosis_content &`

In Example 1, the file **test.csv** contained in the folder **models** has been loaded into the model named **test_model**, using the **SNPs from columns 1 to 10** and setting the **growth_speed** column as the target. Considering this target column is not binary (having values like: fast, medium, slow, very slow, etc.), the **fast** part select the desired label the model will focus on.

In Example 2, the file **rice.csv** contained in the **same folder as EnGENE-Terminal** has been loaded into the model named **model_a**, using the **SNPs from columns 1 to 4000** and setting the **amylosis_content** column as target.

## Train

Description: Trains one or more models the recommended amount of times and calculates their score. If a list of models is given, calculates the cross correlation between the SNPs' scores
Syntax: `Train <modelname or list_of_model_names> &`

*Model_name*: The name assigned to the model that needs training
*List_of_model_names*: A list of model names between brackets []

Example 1: Train test_model &
Example 2: Train [test_model, test_model2, test_model3] &

In Example 1, the model that was loaded with the name **test_model** will be trained 1000 times.
In Example 2, all the models inside the brackets will be trained 1000 times each, and will instantly print the resulting SNPs after a cross-correlation was done between all the models. 

## SNP
Description: Gets a ranked list of snps detected
Syntax: `SNP: <modelname> <n_elements=[all]>`

*Model_name*: The name assigned to the trained model
*N_elements*: The max number of SNPs, in importance order, that should be printed to the screen. If no value is 	specified, all SNPs are printed

Example 1: SNP rice_model 10
Example 2: SNP rice_model

In Example 1, a list of **only the top 10 SNPs found in rice_model** is printed, while Example 2 prints all of the SNPs found.

## The importance of the '&' symbol
In Linux, the '&' symbol is added to the end of a line in the terminal to specify a command that should be run in the background, allowing the user to keep working with the same terminal, even if it's already running something. EnGENE-Terminal implements a training environment, and not a 'wait-to-get-your-files-loaded-and-trained simulator'. Therefore, being in a Linux, Windows or MacOs machine, you'll have the '&' available inside EnGENE.

If you plan on loading a single dataset, then it's okay to run a load command without the & symbol after it. But if you are planning to load several files and don't want to wait for the first one to be done loading to load another one, just put an & symbol at the end of the command and you'll be free to run anything else.

**IT IS HIGHLY RECOMMENDED TO USE THE & SYMBOL IN ANY TRAIN COMMAND**. Since some of these can take several minutes, it's good to be always capable of doing something else while EnGENE trains the models for you. 

**To use the & symbol, just add it to the end of a line as shown in the syntax of the commands**