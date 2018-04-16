# Import PuLP modeler functions
from pulp import *

# Create the 'prob' variable to contain the problem data
prob = LpProblem("BC Transportation Problem 2",LpMinimize)


########################### Set the constants here ###############################################


products = ["Regular","GreenOnion","PartyMix"]
dist_centres = ["Kingman","LasCruces","Provo","Victorville"]
# sites = ["Yuma",'Fresno','Tucson','Pomona','SantaFe','Flagstaff','LasVegas','StGeorge']
sites = ['Tucson','Pomona']
customers = ['SLC','Albuquerque','Phoenix','SanDiego','LosAngeles','Tucson']

site_dist_gas = 0.15
dist_cust_gas = 0.08

# site_dist_distance = [[215,524,672,258],
#                       [444,978,770,243],
#                       [308,276,732,471],
#                       [291,732,617,56],
#                       [531,287,582,766],
#                       [148,477,476,382],
#                       [103,685,377,189],
#                       [222,730,259,306]]

site_dist_distance = [[308,276,732,471], [291,732,617,56]]


dist_cust_distance = [[523,469,195,380,319,308],
                      [823,276,388,695,760,276],
                      [45,555,619,707,645,732],
                      [607,705,358,146,84,471]]


fixed_cost = {'Kingman':6000,'LasCruces':5000,'Provo':8000,'Victorville':9000}

variable_cost = {'Kingman':50,'LasCruces':30,'Provo':60,'Victorville':70}


############################## Set objective function here #######################################


site_dist_choices = LpVariable.dicts("Quantity",(sites,dist_centres,products),0,cat=LpInteger)

dist_cust_choices = LpVariable.dicts("Quantity",(dist_centres,customers,products),0,cat=LpInteger)

y_dist_cust = LpVariable.dicts("Produce or not",(dist_centres,customers,products),0,1,cat=LpInteger)

y_dist = LpVariable.dicts("Construct or not",(dist_centres),0,1,cat=LpInteger)

def get_site_dist_objective(site_dist_distance, site_dist_gas, site_dist_choices):
    obj = 0
    for site_index in range(len(sites)):
        for dist_index in range(len(dist_centres)):
            for product in products: 
                obj += (site_dist_distance[site_index][dist_index] * site_dist_gas) * site_dist_choices[sites[site_index]][dist_centres[dist_index]][product]
    return obj

def get_dist_cust_objective(dist_cust_distance, dist_cust_gas, dist_cust_choices):
    obj = 0
    for dist_index in range(len(dist_centres)):
        for cust_index in range(len(customers)):
            for product in products: 
                obj += (dist_cust_distance[dist_index][cust_index] * dist_cust_gas + variable_cost[dist_centres[dist_index]]) * dist_cust_choices[dist_centres[dist_index]][customers[cust_index]][product]
    return obj

obj = get_site_dist_objective(site_dist_distance, site_dist_gas, site_dist_choices) + \
      get_dist_cust_objective(dist_cust_distance, dist_cust_gas, dist_cust_choices)

for dist_centre in y_dist:
    obj += y_dist[dist_centre] * fixed_cost[dist_centre]

prob += obj, "Total Cost"


########################## Define constraints here #########################################


# Minimum allowable amount of products handled
minimum_products = {'Kingman':1000,'LasCruces':1000,'Provo':2000,'Victorville':2000}

for dist_centre in dist_centres:
    product_total = 0
    for site in sites:
        product_total += sum([site_dist_choices[site][dist_centre][product] for product in site_dist_choices[site][dist_centre]])
    prob += product_total >= minimum_products[dist_centre], (dist_centre+"_Minimum allowable amount of products constraint")

# Maximum allowable amount of products handled
maximum_products = {'Kingman':15000,'LasCruces':12000,'Provo':18000,'Victorville':20000}

for dist_centre in dist_centres:
    product_total = 0
    for site in sites:
        product_total += sum([site_dist_choices[site][dist_centre][product] for product in site_dist_choices[site][dist_centre]])
    prob += product_total <= maximum_products[dist_centre], (dist_centre+"_Maximum allowable amount of products constraint")

# Maximum 50% fraction from site to distibution centre constraint
site_to_dist_ratio = 0.5

for site in sites:
    total = 0
    for dist_centre in dist_centres:
        total += sum([site_dist_choices[site][dist_centre][product] for product in site_dist_choices[site][dist_centre]])
    
    for dist_centre in dist_centres:
        site_to_dist_supply = sum([site_dist_choices[site][dist_centre][product] for product in site_dist_choices[site][dist_centre]])
        prob += (site_to_dist_ratio * total) - site_to_dist_supply >= 0, (site+"_to_"+dist_centre+"_fraction_constraint")

# Demand constraint
demand = [[1300,900,1700],
          [1400,1100,1700],
          [1200,800,1800],
          [1900,1200,2200],
          [1900,1400,2300],
          [1500,1000,1400]]

for cust_index in range(len(customers)):
    for prod_index in range(len(products)):
        demand_constraint = 0
        for dist_centre in dist_centres:
            demand_constraint += dist_cust_choices[dist_centre][customers[cust_index]][products[prod_index]]
        prob += demand_constraint >= demand[cust_index][prod_index], (customers[cust_index] + "'s_" + products[prod_index] + " demand constraint")


# Maximum 60% fraction from distibution centre to customer constraint
dist_to_cust_ratio = 0.6

for dist_centre in dist_centres:
    count = 0
    for customer in customers:
        dist_to_cust_supply = sum([dist_cust_choices[dist_centre][customer][product] for product in dist_cust_choices[dist_centre][customer]])
        cust_demand = sum(demand[count])
        count += 1
        prob += dist_to_cust_supply <= 0.6 * cust_demand, (dist_centre + "_to_" + customer + "_max_fraction_constraint")


# Maximum one product from distribution centre to customer constraint

for dist_centre in dist_centres:
    for customer in customers:
        prob += sum([y_dist_cust[dist_centre][customer][product] for product in y_dist_cust[dist_centre][customer]]) == 1, (dist_centre + "_to_" + customer + " one product constraint")


# Maximum one product logical constraint 

for dist_centre in dist_centres:
    for customer in customers:
        for product in products:
            prob += dist_cust_choices[dist_centre][customer][product] <= y_dist_cust[dist_centre][customer][product] * maximum_products[dist_centre], ""

# non-working distribution logical constraint

for dist_centre in dist_centres:
    product_total = 0
    supply_total = 0
    for site in sites:
        product_total += sum([site_dist_choices[site][dist_centre][product] for product in site_dist_choices[site][dist_centre]])

    for customer in customers:
        supply_total += sum([dist_cust_choices[dist_centre][customer][product] for product in dist_cust_choices[dist_centre][customer]])

    prob += product_total <= y_dist[dist_centre] * maximum_products[dist_centre], ""
    prob += supply_total <= y_dist[dist_centre] * maximum_products[dist_centre], ""


# supply and demand logical constraint for distribution centre

for dist_centre in dist_centres:  
    for product in products:
        total_outgoing_product = 0
        total_incoming_product = 0
        for customer in customers:
            total_outgoing_product += dist_cust_choices[dist_centre][customer][product]

        for site in sites:
            total_incoming_product += site_dist_choices[site][dist_centre][product]

        prob += total_incoming_product == total_outgoing_product, ""


# print(prob)

prob.solve()
print("Status:", LpStatus[prob.status])
for v in prob.variables():
    if v.varValue != 0:
        print(v.name, "=", v.varValue)

print("Total cost:", value(prob.objective))

print("===============================")

end_sum = 0
for site in sites:
    for dist_centre in dist_centres:
        for product in products:
            end_sum += site_dist_choices[site][dist_centre][product].varValue

print("Total outgoing products from site:",end_sum)

dist_to_cust_sum = 0

for dist_centre in dist_centres:
    for customer in customers:
        for product in products:
            dist_to_cust_sum += dist_cust_choices[dist_centre][customer][product].varValue

print("Total outgoing products from distribution centre",dist_to_cust_sum)