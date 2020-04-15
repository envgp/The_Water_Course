import sys
import os

import pandas as pd


'''

Classify crop types from CDL to the faunt scheme 

CDL classes: https://developers.google.com/earth-engine/datasets/catalog/USDA_NASS_CDL
Faunt kc and classes: https://water.usgs.gov/GIS/metadata/usgswrd/XML/pp1766_fmp_parameters.xml 

Dict Key is the Faunt class (int)     
Dict Value is the CDL category (string)

The faunt class = CDL category is shown at the top of each k:v pair. 

'''


cdl2f = {

# Water = water(83), wetlands(87), Aquaculture(92), Open Water(111), Perreniel Ice / Snow (112)
1 : ["83", "87", "92", "111", "112"], 

# Urban = developed high intensity(124), developed medium intensity(123)
2 : ["124", "123"], 

# Native = grassland/pasture(176), Forest(63), Shrubs(64), barren(65, 131), Clover/Wildflowers(58)
# Forests (141 - 143), Shrubland (152)
3 : ["176","63","64", "65", "131","58", "141", "142", "143", "152"], 

# Orchards, groves, vineyards = None
4 : [""],

# Pasture / hay = other hay / non alfalfa (37)
5 : ["37"],

# Row Crops = corn (1), soybeans (5),Sunflower(6) sweet corn (12), pop corn (13), double winter/corn (225), 
# double oats/corn(226), double barley/corn(237), double corn / soybeans
6 : ["1", "5", "6", "12", "13", "225", "226", "237", "239"] ,

# Small Grains = Spring wheat (23), winter wheat (24), other small grains (25), winter wheat / soybeans (26), 
# rye (27), oats (28), Millet(29), dbl soybeans/oats(240)
7 : ["23", "24", "25", "26", "27", "28", "29", "240"] ,

# Idle/fallow = Sod/Grass Seed (59), Fallow/Idle Cropland(61), 
8 : ["59","61"],

# Truck, nursery, and berry crops = 
# Blueberries (242), Cabbage(243), Cauliflower(244), celery (245), radishes (246), Turnips(247)
# Eggplants (249), Cranberries (250), Caneberries (55), Brocolli (214), Peppers(216), 
# Greens(219), Strawberries (221), Lettuce (227), Double Lettuce/Grain (230 - 233)
9 : ["242", "243", "244", "245", "246", "247", "248", "249", "250", "55", "214", "216","219","221", "227", "230", "231", "232", "233"], 

# Citrus and subtropical = Citrus(72), Oranges (212), Pommegranates(217)
10 : ["72", "212", "217"] ,

# Field Crops = 
# Peanuts(10),Mint (14),Canola (31),  Vetch(224),  Safflower(33) , RapeSeed(34), 
# Mustard(35) Alfalfa (36),Camelina (38), Buckwheat (39), Sugarbeet (41), Dry beans (42), Potaoes (43)
# Sweet potatoes(46), Misc Vegs & Fruits (47), Cucumbers(50)
# Chick Peas(51),Lentils(52),Peas(53),Tomatoes(54)Hops(56),Herbs(57),Carrots(206),
# Asparagus(207),Garlic(208), Cantaloupes(209), Honeydew Melons (213), Squash(222), Pumpkins(229), 

11 : ["10",  "14", "224", "31","33", "34", "35", "36", "38", "39", "41", "42", "43", "46", "47", "48" ,
      "49", "50", "51", "52", "53", "54",  "56", "57","206","207", "208", "209","213","222", "229"] ,
    
# Vineyards = Grapes(69)
12 : ["69"],

# Pasture = Switchgrass(60)
13 : ["60"],

# Grain and hay = Sorghum(4), barley (21), Durham wheat (22), Triticale (205), 
# Dbl grain / sorghum (234 - 236), Dbl 
14 : ["4", "21", "22", "205", "234", "235", "236"],

# livestock feedlots, diaries, poultry farms = 
15 : [""],

# Deciduous fruits and nuts = Pecans(74), Almonds(75), 
# Walnuts(76), Cherries (66), Pears(77), Apricots (223), Apples (68), Christmas Trees(70)
# Prunes (210), Plums (220), Peaches(67), Other Tree Crops (71), Pistachios(204), 
# Olives(211), Nectarines(218), Avocado (215)   
16 : ["74", "75", "76","66","77", "223", "68", "210", "220", "67", "70", "71", "204", "211","215","218"],

# Rice = Rice(3)
17 : ["3"],
# Cotton = Cotton (2) , Dbl grain / cotton (238-239)
18 : ["2", "238", "239"], 
# Developed = Developed low intensity (122) developed open space(121)
19 : ["122", "121"],
# Cropland and Pasture
20 : [""],
# Cropland = Other crops (44)
21 : ["44"], 
# Irrigated row and field crops = Woody Wetlands (190), Herbaceous wetlands = 195
22 : ["190", "195"] 
}

num2lc = {1: 'Water',
 2: 'Urban',
 3: 'Native classes',
 4: 'Orchards, groves, and vineyards',
 5: 'Pasture/Hay',
 6: 'Row Crops',
 7: 'Small Grains',
 8: 'Idle/fallow',
 9: 'Truck, nursery, and berry crops',
 10: 'Citrus and subtropical',
 11: 'Field crops',
 12: 'Vineyards',
 13: 'Pasture',
 14: 'Grain and hay crops',
 15: 'Semiagricultural (livestock feedlots, diaries, poultry farms)',
 16: 'Deciduous fruits and nuts',
 17: 'Rice',
 18: 'Cotton',
 19: 'Developed',
 20: 'Cropland and pasture',
 21: 'Cropland',
 22: 'Irrigated Row and Field Crops'}



def main():

	# Read the cdl infile 
	file = sys.argv[1]
	df 	= pd.read_csv(file)

	# Setup out dict 
	fmp = {k: 0 for k in range(1, 1+len(cdl2f))}

	for idx, i in enumerate(df.Value):
		# For each CDL class (keys), find the corresponding FMP class in the cdl2f dict values. 
		for k2,v2 in cdl2f.items():
			# IF the CDL class is in the FMP lookup table values: add the CDL acreage to the fmp outdict
			if str(i) in v2:
				fmp[k2] += df.iloc[:,-1][idx]

	# out_df = pd.DataFrame.from_dict(fmp,  orient='index')
	lclabels = [num2lc[x] for x in fmp.keys()]

	out_df = pd.DataFrame([fmp.keys(),lclabels, fmp.values()]).T
	out_df.columns = ['lc_num','lc_type','acreage']
	

	outfile = file[:-4] + "_processed.csv"
	out_df.to_csv(outfile)
	print("==== Done! ")


if __name__ =="__main__":
	main()

