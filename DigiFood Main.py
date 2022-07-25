#!/usr/bin/env python
# coding: utf-8

# In[227]:


import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import json
import datetime


filename = "transaction-data-adhoc-analysis.json"
rawpivot = pd.DataFrame(pd.read_json(filename))
rawpivot

#rawdata[rawdata["transaction_date"].str.contains("03/")]

#rawdata.sort_values(by='transaction_date', ascending=True, na_position='first')


# # Table: Count per Month

# In[228]:


# Table: Count per Month

rawdata = open(filename,"r+")
df = pd.DataFrame(json.load(rawdata))
   
month = {
        "01/":"JAN",
        "02/":"FEB",
        "03/":"MAR",
        "04/":"APR",
        "05/":"MAY",
        "06/":"JUN"
}

# for every month, itll look for the i in the transaction_date then we label that as the month

for i in month:
    df.loc[df["transaction_date"].str.contains(i),"month"] = month[i]

# function used so that 1): we can check it per month, 2): we can do a for i in the list of month at the end

def monthly_count(mon):
    
    # arranging by month, depending on which "mon" is in the df[mon]
    monthly = df[df.month==mon]
    sorted_df = monthly.sort_values(by=["transaction_date"])

    # item list to separate brands from products from quantities, SAMPLE: 
    # Exotic Extras,Beef Chicharon,(x3);HealthyKid 3+,Nutrional Milk,(x4);
    # INTO THIS:
    # Exotic Extras  Beef Chicharon    x3 
    # HealthyKid 3+  Nutritional Milk  x4
    item_list = []
    for index,row in sorted_df.iterrows():
        product_split = (row["transaction_items"].split(";"))
        for i in range(0,len(product_split)):
            item_list.append(product_split[i].split(","))
    
    
    item_df = pd.DataFrame(item_list,columns=["BRAND","PRODUCT","QUANTITY"])
    item_df["QUANTITY"] = item_df["QUANTITY"].str.extract('(\d+)',expand=False)
    item_df["QUANTITY"] = item_df["QUANTITY"].astype(int)

    itemcount = item_df.groupby("PRODUCT").sum()
   
    return itemcount.squeeze()

product_sale_count_df = pd.DataFrame({i:monthly_count(i) for i in list(month.values())})

product_sale_count_df
        


# # Table: Total Sale Value per Item per Month

# In[229]:


# Table: Total Sale Value per Item per Month

# for some reason, i couldn't separate them to make the code more readable: like so
    # all_salevaluedf = df[["transaction_items","transaction_value"]]
    # all_salevaluedf.drop_duplicates(subset=["transaction_items"])
# i actually couldn't understand why it didnt work, so i joined them together

all_salevaluedf = df[["transaction_items","transaction_value"]].drop_duplicates(subset=["transaction_items"])

unique_salevaluedf = pd.DataFrame(all_salevaluedf.loc[all_salevaluedf["transaction_items"].str.contains("x1") 
                                                      & (all_salevaluedf["transaction_items"].str.contains(";")== False)])

# concept: change the index of the column names, moving it to the appropriate column
def count_items_index(value):
    count_index = value[value.index(",")+1:value.index(",",value.index(",")+1)]
    return count_index

# applying index change
unique_salevaluedf["Product Name"] = unique_salevaluedf["transaction_items"].apply(count_items_index)

# getting cost of each item from respective product
cost = unique_salevaluedf.set_index("Product Name")["transaction_value"]

# labeling cost with respective name
total_revenue = pd.DataFrame({"Cost for each product":cost})

# for each i in  the total number of i's in the keys of product_sale_count_df, 
# we multiply the i'th value of the cost of the total revenue by the i'th value of the products_sale_count_df

for i in tuple(product_sale_count_df.keys()):
    total_revenue[i] = total_revenue["Cost for each product"] * product_sale_count_df[i]
    
total_revenue = total_revenue[["Cost for each product","JAN","FEB","MAR","APR","MAY","JUN"]]

total_revenue


# # Pie Chart for Monthly Sold Goods

# In[230]:


# to show which one is in most demand for each month, so the next month's supplies 
# could be adjusted accordingly

#additional note while grading this part, this actually took me too long it took me so many stackoverflow articles and
#this article in particular: https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/

def pie_chart(mon):
    pie_items = ["Yummy Vegetables","Gummy Worms","Beef Chicharon","Kimchi and Seaweed","Orange Beans","Gummy Vitamins","Nutrional Milk",
                 ]
    pie_slices = [i for i in product_sale_count_df[mon]]
    colors = ["red","yellow","blue","cyan","magenta","orange","green"]
    plt.pie(pie_slices,labels=pie_items,colors=colors,startangle=90,shadow=True,explode = (0,0,0,0,0,0,0),
            radius = 1.2, autopct='%1.3f%%')
    plt.legend(bbox_to_anchor=(1,0.5), loc="center right", fontsize=9, 
           bbox_transform=plt.gcf().transFigure)
    plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
    plt.title("Monthly distribution of bought goods for: "+mon)
    plt.show()


# In[231]:


pie_chart("JUN")


# # Repeaters

# In[335]:


# Repeaters

def repeater(mon):
    month_l = ["JAN","FEB","MAR","APR","MAY","JUN"]
    month_index = month_l.index(mon)
    
    monthofinterest = df[df["month"]==month_l[month_index]]
    monthPrior_ofinterest = df[df["month"]==month_l[month_index-1]]
    
    MOI = set(monthofinterest["username"])
    MPOI = set(monthPrior_ofinterest["username"])
    return len(MOI & MPOI)


# In[361]:


repeater("JAN")


# In[362]:


repeater("FEB")


# In[363]:


repeater("MAR")


# In[364]:


repeater("APR")


# In[365]:


repeater("MAY")


# In[366]:


repeater("JUN")


# # Inactives

# In[353]:


# Inactives
month_l = ["JAN","FEB","MAR","APR","MAY","JUN"]

def inactive(mon):
    month_number = month_l.index(mon)+1
    january = set(df[df["month"].str.contains("JAN")]["name"])
    february = set(df[df["month"].str.contains("FEB")]["name"])
    march = set(df[df["month"].str.contains("MAR")]["name"])
    april = set(df[df["month"].str.contains("APR")]["name"])
    may = set(df[df["month"].str.contains("MAY")]["name"])
    june = set(df[df["month"].str.contains("JUN")]["name"])
    notjanuary = set(df[~df["month"].str.contains("JAN")]["name"])
    notfebruary = set(df[~df["month"].str.contains("FEB")]["name"])
    notmarch = set(df[~df["month"].str.contains("MAR")]["name"])
    notapril = set(df[~df["month"].str.contains("ARP")]["name"])
    notmay = set(df[~df["month"].str.contains("MAY")]["name"])
    notjune = set(df[~df["month"].str.contains("JUN")]["name"])

    conditions = set()
    if month_number == 1:
        pass
    elif month_number == 2:
        conditions = (january & notfebruary)
    elif month_number == 3:     
        conditions = (january & february & notmarch)
    elif month_number == 4:   
        conditions = (january & february & march & notapril)
    elif month_number == 5:   
        conditions = (january & february & march & april & notmay)
    elif month_number == 6:   
        conditions = (january & february & march & april & may & notjune)
    else:
        return len(conditions)


# In[369]:


inactive("JAN")


# In[368]:


inactive("FEB")


# In[370]:


inactive("MAR")


# In[371]:


inactive("APR")


# In[372]:


inactive("MAY")


# In[373]:


inactive("JUN")


# # Engaged
# 

# In[327]:


#engaged: 
month_l = ["JAN","FEB","MAR","APR","MAY","JUN"

def engaged(mon):
    month_number = month_l.index(mon)+1
    january = set(df[df["month"] == "JAN"]["name"])
    february = set(df[df["month"] == "FEB"]["name"])
    march = set(df[df["month"] == "MAR"]["name"])
    april = set(df[df["month"] == "APR"]["name"])
    may = set(df[df["month"] == "MAY"]["name"])
    june = set(df[df["month"] == "JUN"]["name"])

    conditions = set()
    if month_number == 1:
        conditions = january
    elif month_number == 2:   
        conditions = (january & february)
    elif month_number == 3:     
        conditions = (january & february & march)
    elif month_number == 4:   
        conditions = (january & february & march & april)
    elif month_number == 5:   
        conditions = (january & february & march & april & may)
    elif month_number == 6:   
        conditions = (january & february & march & april & may & june)
    else:
        pass
    if len(conditions) == 0:
        return (f"Not a valid month!")
    else:
        return len(conditions)


# In[374]:


engaged("JAN")


# In[375]:


engaged("FEB")


# In[376]:


engaged("MAR")


# In[377]:


engaged("APR")


# In[378]:


engaged("MAY")


# In[379]:


engaged("JUN")


# In[ ]:




