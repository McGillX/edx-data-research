'''
This module retrieve IP addresses for each student and maps their IP to a country
This is to determine the diversity of students who took a given course
The geoip module and GeoIP.dat file was used to map the IP address to a country

Each user may have multiple ips, so this module retrieves all the countries mapped to those ips
Disclaimer: The accuracy of the IP to Country cannot be determined as it is difficult to determine
if the IP is an actual IP or a proxy IP

At the end of the analysis, the results are used to create a Pie Chart to visualize the distribution

Usage:
python ip_to_country.py <db_name>

'''
import geoip
import csv
from collections import defaultdict


def ip_to_country(edx_obj):
    edx_obj.collections = ['tracking']
    with open('reporting/basic/country_code_to_country.csv') as csv_file:
        reader = csv.reader(csv_file)
        country_code_to_country = dict(reader)
    cursor = edx_obj.collections['tracking'].find()
    result = defaultdict(set)
    for index, item in enumerate(cursor):
        result[item['username']].add(item['ip'])
    ip_to_country = []
    country_set = set()
    for key, value_set in result.iteritems():
        for value in value_set:
            try:
                country_code = geoip.country(value, dbname='reporting/basic/GeoIP.dat')
                country = country_code_to_country[country_code]
                if not key:
                    key = 'anonymous'
                    ip_to_country.append([key, value, country_code, country])
                elif (key, country) not in country_set:
                    country_set.add((key,country))
                    ip_to_country.append([key, value, country_code, country])
            except:
                # IMPORTANT
                # The following code for an exception are hardcoded for those IPs which do have a mapping to a 
                # country code but they were not available in GeoIP.dat (most probably because it was not updated)
                # People using this script can either report this code (under except) and or additional conditions
                # IP addresses which cannot be mapped to a country code stored in GeoIP.dat
                if value == '41.79.120.29':
                    country = country_code_to_country['SS']
                    if not key:
                        key = 'anonymous'
                        ip_to_country.append([key, value, 'SS', country_code_to_country['SS']])
                    elif (key, country) not in country_set:
                        country_set.add((key, country))
                        ip_to_country.append([key, value, 'SS', country_code_to_country['SS']])
    edx_obj.generate_csv(ip_to_country, ['Username', 'IP Address', 'Country Code', 'Country'], output_file=edx_obj.db.name+'_ip_to_country.csv')
