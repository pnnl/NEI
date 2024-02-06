#%% README

"""
1) Installing Python and Anaconda

For most data science work it is recommended to purchase Anaconda, which is a distribution and package manager 
for Python and the major data science libraries. It used to be free for research, but now you must purchase it 
through the PNNL App store. If you don't want to purchase it or don't want such a large environemnt for Python,
then you can download just "miniconda," which is a condensed version of Anaconda. You could also just install
Python directly and use the Python package manager 'pip' to install just what you need with the command prompt.
It is not recommended to mix and match these different options though.

2) Installing an IDE vs. Jupyter

I prefer the Spyder IDE, which is pretty similar to RStudio, but another popular option is PyCharm. Jupyter
notebooks are another popular way to write and share code, as they integrate with your browser and make it simple
to share notebooks without something like git. They are also good for visualizations. Not recommended for shared
work or maintaining a code base though, and they are more difficult to debug.

3) Creating virtual environments

Managing verions of Python and associated libraries you are using for a particular project can be a challenge, so 
it is recommended to create virtual environments for each project. This will keep all your package versions consistent.
Use the Anaconda Navigator to create a new environment, or if you do not have Navigator then use 'venv' in the command
prompt to create and activate a new environment.

4) Installing packages with pip or conda

Use Anaconda Navigator to easily install the packages you will need in your environment, but you probably won't need
the full list it comes with. If you are using miniconda, you would install packages with the 'conda' package manager
in the command prompt or an Anaconda prompt. Otherwise, use pip in the command prompt to install packages in the 
appropriate environment.

5) Basic Python use tips

The template below shows the general structure of a Python script. Some additional tips include:
- Indentation is needed to define structures of functions and loops. No curly brackets or semicolons needed.
- There is an eternal debate on whether to use tabs or spaces for indentation. I prefer tabs, but either way just
be consistent.
- Don't reinvent the wheel, there are many built-in functions that do many common tasks. Check if it's already been done.
- Use the print() function to print to console.
- Assign variables with "=", not with this sillyness "<-".
- # designates a comment, #%% creates a cell. You can run cells individually, which is useful when analyzing data.
- Use F9 in Spyder to run a single line of code, or a selection of code.
- Arrays are zero-indexed, so counting always starts with 0 and not 1.
- "" and '' both work the exact same for text strings. 
- Triple quotes (like at the start and end of this text) turn everything between into a string, which is useful for
long comments. If you add triple quotes after a function it creates a docstring for that function.
- Adding an r"" in front of quotes turns it into raw text, which is useful for filepaths. Adding an f"" allows for
formatting capability within the string, for example: 
    name = "Max"
    print(f"My name is {name}.") # this would print My name is Max.
- When possible, use list comprehension instead of for loops. There's an example below.
- If using Spyder, doubleclick on a variable in the explorer to open it in a popup, makes viewing dataframes easier.
- Python supports procedural, functional, and object-oriented programming. Functional runs the fastest and is the
easiest to read and write (in my opinion) but you'll see all three regularly.

6) Version control with GitHub

- First step is to create an account on GitHub. Next, download git (the language). This is typically run in the command
prompt, but you can download GitHub Desktop if you prefer a GUI. GitHub also has a built in editor but it is not recommended
for major work.
- Clone the repo, the address is https://github.com/pnnl/NEI
- Typically if you are making significant changes to the code you would create a branch off of main, this way you can work
with the current code without affecting it for other users. Name the branch something relevant to what you're working on.
- After making your changes/additions, commit them to your branch by first adding the changed files in git, then committing
with a commit message that describes what you did.
- When you are ready, push your updated code to your branch on the repo.
- When you are done with making changes, merge the branch back to main. This will highlight all the changes and additions
to the code, and the repo admin will accept or reject them. This will then be the latest code version.
- Unless you are going to make more updates, you can delete your branch when you are done.
- Use pull on the repo to make sure you have the latest version of code before doing any new work. Sometimes conflicts
will occur, which requires you to manually fix the differences between the two versions of code.

Here are some guides on typical git usage and commands:

https://rogerdudler.github.io/git-guide/
https://github.com/abduvik/just-enough-series/tree/master/courses/git

"""

#%% import useful libraries into a Python scrypt with import. You can use an alias with "as" so you don't have to
# keep writing the full name of the library. Use "from" to import just the specific functions or methods you want
# from a library, this can save on run time.

import os # built-in functions for working with the Windows system
from datetime import datetime as dt # library for getting and working with dates and time
from glob import glob # useful module for pattern matching and batch operations
import pandas as pd # most popular data science library for working with panel/tabular data
import numpy as np # most popular computational library, used in the backend of pandas
import scipy as sp # for more complex computational operations
import statsmodels.api as sm # for more advanced statistical testing
import matplotlib.pyplot as plt # popular plotting library
import seaborn as sns # wrapper for matplotlib to make plotting much easier
from sklearn import linear_model # scikit-learn is a very useful machine learning library with many models built in
#import torch # pytorch and tensorflow are both very powerful deep learning libraries for more advanced machine learning models
#import tensorflow as tf # they currently do not work with the latest Python version however

#%% read in data and create a pandas dataframe
# don't forget escape character "\" in file paths

username = os.getlogin() # get your active username
share_path = fr"C:\Users\{username}\\" # insert your username in the file path

path = os.getcwd() # this will get your current active folder, or you can type it directly with r"C:\path\to\folder\etc\\"
file = r"RED_data_rf.csv" # if you set your current folder to the directory where the file is located (in the top right of Spyder) then all you need is the file name
filepath = os.path.join(path, file) # add the file to the folder path
df = pd.read_csv(filepath) # read the file at the speicifed filepath into a pandas dataframe

#%% open, examine, and select data

df_stats = df.describe() # descriptive statistics on each column

# find and remove NaNs
nans = df.isnull().sum() # check how many nans are in each column
df_no_nans = df.dropna() # removes all nans, or can set thresh to limit how many nans are needed to drop that row or column
df_nans_filled = df.fillna(0).astype("int") # replace all nans with a value (useful for plotting, sometimes nans break matplotlib)

df_sel_col_name = df[["homesize", "yearsinhome", "heatpumpHVAC"]] # select columns by name
df_sliced_name = df.loc[:, "yearbuilt" : "yearsinhome"] # slice by the name of the columns, ":" by itself means "all" rows or columns
df_sliced_idx = df.iloc[0:100, 2:5] # slice the dataframe by index [rows, columns]
df_sliced_conditional = df.loc[(df.loc[:, "heatpumpwh"] == 1)] # select rows if a column is equal to a certain value

df_heatpumpwh_transposed = df_sliced_conditional.T # transpose a dataframe so rows are now columns

#%% basic Pythonic operations

# define a simple function
def age_count_for_loop(df, threshold):
    """
    Count all participants over the threshold age.
    """
    
    i = 0
    for age in df["age"]:
        if age > threshold:
            i += 1
            
    return i

# list comprehension is a Python technique that can replace a for loop while making a list
list_comp = [i for i in df.columns]

# e.g., the list comprehension below does the same thing as the for loop in the previous function
def age_count_list_comp(df, threshold):
    
    i = 0
    [i := i + 1 for age in df["age"] if age > threshold]
    
    return i

age_with_loop = age_count_for_loop(df, 65)
age_with_listcomp = age_count_list_comp(df, 65)
print(age_with_loop == age_with_listcomp) # both functions should return the same value

# you can use a switch-case statement instead of an if-else iteration (only for Python versions 3.10+)
def has_heatpump(df):
    """
    Check what type of heat pump a participant has.
    """
    
    match (df["heatpumpwh"], df["heatpumpHVAC"]):
        case (0, 0):
            return "None"
        case (1, 0):
            return "Water Heater"
        case (0, 1):
            return "HVAC"
        case (1, 1):
            return "Both"
        case _:
            return "Unknown"

# lambda creates a local function that can be applied in one line. axis = 1 applies function to columns, and 0 to rows
df["heatpump"] = df.apply(lambda df: has_heatpump(df), axis = 1) # create a new column in the dataframe called "heatpump"

# dictionaries are a Python data structure similar to JSON, they can store any type of data in key-value pairs
number_heatpumps_dict = {
                        "Both": sum(df["heatpump"] == "Both"),
                        "HVAC": sum(df["heatpump"] == "HVAC"),
                        "Water Heater": sum(df["heatpump"] == "Water Heater"),
                        "None": sum(df["heatpump"] == "None"),
                        "Unknown": sum(df["heatpump"] == "Unknown")
                        }

# dictionary comprehension can create a dictionary similar to how list comprehension works, the code below does the same thing as the previous dict
number_heatpumps_dict_comp = {df["heatpump"].value_counts().index[i]: df["heatpump"].value_counts().iloc[i] for i in range(len(df["heatpump"].value_counts()))}

#%% plot the data with seaborn and matplotlib

# create a plot of education vs. income
sns.lineplot(data = df, x = df["education"], y = df["income"])
plt.show() # display the plot in the IDE
plt.clf() # clear the plot from active memory to show the next one

# create a boxplot of income and customize the visual properties and labels
sns.boxplot(data = df["income"], width = 0.25,
            boxprops = {"facecolor": "lightsteelblue", "edgecolor": "black"},
            medianprops = {"color": "r","linewidth": 2},
            whiskerprops = {"color": "black"},
            flierprops = {"marker": "x"}
            )
plt.title("Income")
plt.xlabel("All")
plt.xticks([])
plt.ylabel("$")
plt.show()
plt.clf()

# create a pivot table and plot a heat map
category_order = ["Both", "HVAC", "Water Heater", "None"] # set order for labels, otherwise default is alphabetical/ascending
df_pivot = pd.pivot_table(data = df, index = "heatpump", columns = "education", values = "income").reindex(category_order)
sns.heatmap(data = df_pivot, cmap = "Spectral_r") # set the color palette with cmap, there are many built-in color options
plt.title("Income")
plt.show()
plt.savefig("income_heatmap.jpeg") # save the plot as an image in your current folder
plt.clf()

#%% save output as a csv file

df_to_save = df_heatpumpwh_transposed

current_date = dt.today().strftime("%m-%d-%y")
save_file_name = f"Results_{current_date}.csv"
save_path = os.path.join(path, save_file_name)

df_to_save.to_csv(save_path)

