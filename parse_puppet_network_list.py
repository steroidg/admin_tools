#!/usr/bin/python

# This script sorts a comma separated list by its first field which is FQDN
# It's not useful for anything else but hay...
#
# Author: Dinan Yin

puppet_network_list_file="/tmp/puppet_network_list.txt";
try:
	p_file = open(puppet_network_list_file, "r");
except IOError: 
	print "Error: Unable to open file: {0}".format(puppet_network_list_file);
	exit (1);
p_content = p_file.readlines();
p_file.close();

sort_array = [];
sort_array_index=0;
for i in p_content:
	i_fqdn="";
	i_fqdn=i.split(",")[0].strip().split(".");
	i_fqdn.reverse();
	i_array=[i_fqdn, sort_array_index];
	sort_array.append(i_array);
	sort_array_index += 1;

final_array = [];
sort_array.sort();
for i in sort_array:
	final_array.append(p_content[i[1]]);

dest_file_name = "/tmp/dest_file";
try:
	d_file = open (dest_file_name, "w");
except IOError: 
	print "Error: Unable to open file: {0}".format(puppet_network_list_file);
	exit (1);

for i in final_array:
	d_file.write(i);
d_file.close();


exit (0);
