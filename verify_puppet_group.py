#!/usr/bin/python
'''
Created on 13/11/2012

@author: Dinan Yin
'''
import glob
import os
import sys
import smtplib


def send_email (report_msg):
    from_addr="root@puppetmaster-cbr.it.csiro.au"
    to_addrs="leh015@csiro.au, rea094@csiro.au, yin006@csiro.au"
#    to_addrs="yin006@csiro.au, leh015@csiro.au"
    msg = "From: {0}\r\nTo: {1}, \r\nSubject:puppet group report\r\n\r\n".format(from_addr, to_addrs)
    msg += report_msg
    try:
        server = smtplib.SMTP('smtp.csiro.au')
        server.sendmail(from_addr, to_addrs.split(), msg)
        server.quit()
    except (smtplib.socket.error, smtplib.SMTPException):
        pass

# Verify that the group file is following the correct format
# The current format is "^node '<host_name>' { <group_name> }\n"
def process_group_file (group_file, pem_file_list):
    g_file = open(group_file, "r")
    problem_lines=""
    group_file_split = group_file.split("/")
    group_file_name = group_file_split[len(group_file_split) - 1].split(".")[0]
    
    j = 1
    for i in g_file:
        if (i.startswith("node")):
            syntax_error=""
            if not (i.endswith("}\n")):
                syntax_error+="    syntax issue: line not terminated with }\n";
                
            included_group=i.split("include")[1].split(" ")[1]
            if not (included_group == group_file_name):
                syntax_error+="    syntax issue: included group mismatch {0} != {1}.pp\n".format(included_group, group_file_name);
 
            if (syntax_error):
                problem_lines+="  line {0} > {1}".format(j, i);
                problem_lines+=syntax_error;
                
            host_pem_filename="{0}.pem".format(i.split("'")[1])
            match_found=False
            for k in pem_file_list:
                split=k.split("/")
                pem_filename=split[len(split) - 1]
                if (host_pem_filename == pem_filename):
                    match_found=True
            if not (match_found):
                problem_lines+="  line {0} > unable to find signed key {1}\n".format(j, host_pem_filename)
        j+=1
    g_file.close()
    return (problem_lines)


# Check if a pem file has a group entry
# return boolean value of whether pem file has entry (True) or not (False)
def pem_file_check (pem_file, group_file_list):
    pem_has_entry = False
    pem_name_split=pem_file.split("/")
    pem_name=pem_name_split[len(pem_name_split) - 1]
    for i in group_file_list:
        g_file = open(i, "r")
        for j in g_file:
            if (j.startswith("node")):
                host_name=j.split("'")[1]
                host_name+=".pem"
                if (pem_name == host_name):
                    pem_has_entry = True 
        g_file.close()
    return (pem_has_entry)


# This is the main function
# Returns exit code in int
def main():
    if (len(sys.argv) != 1):
        print "ERROR: Incorrect number of arguments."
        return 1
        
    # init variables
    puppet_group_dir="/etc/puppet/groups"
    puppet_pem_dir="/var/lib/puppet/ssl/ca/signed"
    report_msg=""
    
    if not os.path.isdir(puppet_group_dir):
        print "ERROR: {0} directory not found.".format(puppet_group_dir)
        return 1

    if not os.path.isdir(puppet_pem_dir):
        print "ERROR: {0} directory not found.".format(puppet_pem_dir)
        return 1
        
    puppet_group_files_path = glob.glob(os.path.join(puppet_group_dir, '*.pp'))
    puppet_pem_files_path = glob.glob(os.path.join(puppet_pem_dir, '*.pem'))
    n_gfile = len(puppet_group_files_path)
    
    # Loop to process group format
    i = 0;
    group_format_ret = ""
    while (i < n_gfile):
        group_format_ret = process_group_file (puppet_group_files_path[i], puppet_pem_files_path)
        if (len(group_format_ret) > 0):
            report_msg += "file: {0}\n".format(puppet_group_files_path[i])
            report_msg += "{0}".format(group_format_ret)
        i+=1
        
    
    # Loop to check if signed ssl keys are in the group or not
    n_pfile = len(puppet_pem_files_path)
    i = 0;
    while (i < n_pfile):
        pam_file_has_group_entry = pem_file_check(puppet_pem_files_path[i], puppet_group_files_path)
        if not (pam_file_has_group_entry):
            report_msg += "pamfile: {0} has no group entry\n".format(puppet_pem_files_path[i])
        i+=1
        
    if (len(report_msg) > 0):
        send_email(report_msg)
#        print "{0}".format(report_msg)
    else:
#        print "Nothing to report"
        return 0
    
exit(main())
