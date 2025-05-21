### use this script to combine 
# all csv files into a single csv file

# if you don't have dplyr, purr, or rstudioapi installed
## uncomment lines 6-8
## install.packages("dplyr")
## install.packages("purrr")
## install.packages("rstudioapi")

# libraries required
library(dplyr)
library(purrr)
library(rstudioapi)

# make sure that combine_files.R and 
# all data files in same folder
# set wd - works for anyone using rstudioapi
setwd(dirname(getActiveDocumentContext()$path))

#### get list of files
files <- list.files(pattern="*.csv") 

for(file in files)
{
  perpos <- which(strsplit(file, "")[[1]]==".")
  assign(
    gsub(" ","",substr(file, 1, perpos-1)), 
    read.csv(paste(file,sep="")))
}


# combine all files into a single dataframe df
df <- list(home_demographics,
           barriers,
           budget, 
           considerations, 
           counts_changes_willingness,
           geography,
           home_mods,
           home_mods_landlord,
           household_preferences,
           info_sources,
           programs, 
           purchase_preferences, 
           repairs, 
           scenarios) %>% 
  reduce(inner_join, by = "PermNum")



# create UPGRADE_E dataset 
# comment out lines 56-57
# if you do not want to write 
# df to your computer as a .csv)

write.csv(df, "UPGRADE-E.csv",
          row.names = FALSE, na = "")


