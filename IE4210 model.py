# Import PuLP modeler functions
from pulp import *

# Create the 'prob' variable to contain the problem data
prob = LpProblem("BC Transportation Problem",LpMinimize)

products = ["Regular","GreenOnion","PartyMix"]
materials = ["Corn","Wheat","Potato"]
sites = ["Yuma",'Fresno','Tucson','Pomona','SantaFe','Flagstaff','LasVegas','StGeorge']
customers = ['SLC','Albuquerque','Phoenix','SanDiego','LosAngeles','Tucson']

GAS_MONEY = 0.15
DISTANCE = [[715, 651, 197, 173, 283, 249],
            [813, 912, 591, 359, 220, 703],
            [776, 449, 113, 407, 485, 0],
            [660, 759, 345, 115, 30, 457],
            [625, 64, 480, 832, 848, 512],
            [519, 323, 145, 488, 464, 257],
            [421, 572, 298, 333, 271, 410],
            [302, 528, 412, 450, 388, 524]]

MATERIAL_COST = [[10,5,16],
                 [12,8,11],
                 [9,10,15],
                 [11,7,14],
                 [8,14,10],
                 [10,12,11],
                 [13,12,9],
                 [14,15,8]]

FIXED_COST = {'Yuma':125000,'Fresno':130000,'Tucson':140000,'Pomona':160000,'SantaFe':150000,
              'Flagstaff':170000,'LasVegas':155000,'StGeorge':115000}

def getProductMix(MATERIAL_COST):
    regular_ratio = (0.7,0.2,0.1)
    green_onion_ratio = (0.3,0.15,0.55)
    party_mix_ratio = (0.2,0.5,0.3)
    product_mix = []
    
    for site in MATERIAL_COST:
        regular = sum([regular_ratio[i]*site[i] for i in range(len(site))])
        green_onion = sum([green_onion_ratio[i]*site[i] for i in range(len(site))])
        party_mix = sum([party_mix_ratio[i]*site[i] for i in range(len(site))])
        product_mix.append([regular,green_onion,party_mix])
    return product_mix

def getOverallCost(distance, productMix, gas_money):
    overallCosts = {}
    for site in range(len(distance)):
        sitesCosts = {}
        for customer in range(len(distance[site])):
            siteCosts = {}
            for material in range(len(productMix[site])):
                siteCosts[products[material]] = (round(distance[site][customer]*gas_money + productMix[site][material],2))
            sitesCosts[customers[customer]] = (siteCosts)
        overallCosts[sites[site]] = (sitesCosts)
    return overallCosts

def getObjective(variables, weights):
    obj = 0
    for site in variables:
        for customer in variables[site]:
            for product in variables[site][customer]:
                obj += weights[site][customer][product] * variables[site][customer][product]
    return obj

overallCosts = getOverallCost(DISTANCE, getProductMix(MATERIAL_COST), GAS_MONEY)

choices = LpVariable.dicts("Choice",(sites,customers,products),0,cat=LpInteger)

y = LpVariable.dicts("Choice",(sites),0,1,cat=LpInteger)

# define objective here
obj = getObjective(choices,overallCosts)

for site in y:
    obj += y[site]*FIXED_COST[site]

prob += obj, "Total Cost"

# Site Production constraint
for site in choices:
    prodConstraint = 0
    for customer in choices[site]:
        for product in choices[site][customer]:
            prodConstraint += choices[site][customer][product]
    prob += prodConstraint <= 20000, (site + " production constraint")

# Customer Demand constraint
demand = [[1300,900,1700],
          [1400,1100,1700],
          [1200,800,1800],
          [1900,1200,2200],
          [1900,1400,2300],
          [1500,1000,1400]]


for cusIndex in range(len(customers)):
    for prodIndex in range(len(products)):
        demandConstraint = 0
        for site in sites:
            demandConstraint += choices[site][customers[cusIndex]][products[prodIndex]]
        prob += demandConstraint >= demand[cusIndex][prodIndex],\
                (customers[cusIndex] + "'s " + products[prodIndex] + " demand constraint")


# Fixed cost constraint
for site in choices:
    fixedCostConstraint = 0
    siteProductionTotal = 0
    for customer in choices[site]:
        for product in choices[site][customer]:
            siteProductionTotal += choices[site][customer][product]
    prob += siteProductionTotal - y[site]*20000 <= 0, (site + " Fixed Cost constraint")


# Site State constraint
prob += y['LasVegas'] + y['SantaFe'] + y['StGeorge'] + \
        (1 if y['Yuma'] == 1 or y['Tucson'] == 1 or y['Flagstaff'] == 1 else 0) + \
        (1 if y['Fresno'] == 1 or y['Pomona'] == 1 else 0) <= 2, "Site state constraint"



prob.solve()
print("Status:", LpStatus[prob.status])
for v in prob.variables():
	if v.varValue != 0:
		print(v.name, "=", v.varValue)

print("Total cost:", value(prob.objective))
