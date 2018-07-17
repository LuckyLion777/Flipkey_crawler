import urllib2
import datetime
from bs4 import BeautifulSoup
import time
import pytz
import csv, os, re, sys, getopt
from dateutil import parser
import xml.etree.cElementTree as ET

g_outputfile = "result.csv"
g_log_file = "log.txt"
g_max_log_lines = 10000
g_idx_for_log = 0
g_old_item_no = 0
g_isfilevalid = False
g_statusfilename = "status.txt"

g_view_from = 1
g_view_to = 114638

def CDATA(text=None):
    text = "<![CDATA[%s]]>" % text
    return text

def print_to_log(str_to_log):
    #write a log file
    print(str_to_log)
    global g_log_file, g_max_log_lines, g_idx_for_log
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    g_idx_for_log += 1
    fo = open(g_log_file, "a")
    try:
        #str_to_log += "----------log line cnt: %s" % g_idx_for_log
        str_to_log = str_to_log.encode("utf8", "ignore")
        fo.write( st + "\t: " + str_to_log + "\n" )
    except:
        pass
    fo.close()
    if g_idx_for_log >= g_max_log_lines:
        open(g_log_file, 'w').close()
        g_idx_for_log = 0

def process_one_page(page_url, item_idx):
    global g_outputfile, g_statusfilename
    global g_old_item_no
    rtn = False

    print_to_log("processing>>> item_idx: %s, page_url: %s" % (item_idx, page_url))
    req = urllib2.Request(page_url)
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        #print e
        print_to_log("Can't find this page. Maybe this is not valid user.")
        return rtn

    result = response.read()
    #print result
    t_soup = BeautifulSoup(result,'lxml')
    #print(t_soup.prettify())

    #write status file
    fo = open(g_statusfilename, "wb")
    strtemp = "item_no=%s" % (item_idx)
    fo.write( strtemp)
    fo.close()

    t_NumberOfProperties = ""
    t_CompanyWebsite = ""
    t_CompanyFacebookPage = ""
    t_CompanyPhoneNumber = ""
    t_LocationOfCompanyUser = ""
    t_TopText = ""
    t_BadgeContainerProperties = ""
    t_NumberOfReviews = ""

    try:
        t_tags = t_soup.findAll('span', attrs={'id':'prop_count'})
        t_NumberOfProperties = ''.join(t_tags[0].findAll(text=True) ).replace('\r\n', ' ')
    except:
        pass

    try:
        t_tags = t_soup.findAll('a', text="Company website")
        t_CompanyWebsite = t_tags[0].get('href')
    except:
        pass

    try:
        t_tags = t_soup.findAll('a', text="Facebook")
        t_CompanyFacebookPage = t_tags[0].get('href')
    except:
        pass

    try:
        t_tags = t_soup.findAll('div', attrs={'id':'fd_sidebar'})
        str = ''.join(t_tags[0].findAll(text=True) ).replace('\r\n', ' ')
        #print_to_log(str)
        #html_str = t_tags.prettify()

        #t_CompanyPhoneNumber
        p = re.compile(r'Phone number:\n(?P<param>.*)\n')
        m = p.search( str )
        if m is not None and m.group('param') is not None:
            t_CompanyPhoneNumber = m.group('param')
            t_CompanyPhoneNumber = t_CompanyPhoneNumber.strip()

        #t_LocationOfCompanyUser
        p = re.compile(r'Office located in:\n\n(?P<param>.*)\n')
        m = p.search( str )
        if m is not None and m.group('param') is not None:
            t_LocationOfCompanyUser = m.group('param')
            t_LocationOfCompanyUser = t_LocationOfCompanyUser.replace('\n','')
            t_LocationOfCompanyUser = t_LocationOfCompanyUser.strip()

        #t_NumberOfReviews
        p = re.compile(r'(?P<param>\d+) reviews')
        m = p.search( str )
        if m is not None and m.group('param') is not None:
            t_NumberOfReviews = m.group('param')
            t_NumberOfReviews = t_NumberOfReviews.strip()

    except:
        pass

    try:
        t_tags = t_soup.findAll('div', attrs={'id':'fd_summary_text','class':'fd_top_content'})
        t_divs = t_tags[0].findAll('div')
        t_ps = t_divs[0].findAll('p')
        t_TopText = ''.join(t_ps[0].findAll(text=True) ).replace('\r\n', ' ')
        t_TopText = t_TopText.strip()
    except:
        pass

    try:
        t_tags = t_soup.findAll('div', attrs={'class':'fd-badge-container'})
        t_BadgeContainerProperties = ""
        for t_tag in t_tags:
            str = ''.join(t_tag.findAll(text=True) ).replace('\r\n', ' ')
            if len(str.strip()) > 0:
                if len(t_BadgeContainerProperties) > 0:
                    t_BadgeContainerProperties += ","
                t_BadgeContainerProperties += str.strip()
    except:
        pass

    if len(t_NumberOfProperties)<1 and len(t_CompanyWebsite)<1 and len(t_CompanyPhoneNumber)<1 and len(t_LocationOfCompanyUser)<1 and \
                    len(t_BadgeContainerProperties)<1 and len(t_NumberOfReviews)<1:
        print_to_log("Can't find this page. Maybe this is not valid user.")
        return rtn

    fdWriter = csv.writer(open(g_outputfile, 'ab'))
    fdWriter.writerow([item_idx,page_url,t_NumberOfProperties.encode('utf8'),t_CompanyWebsite.encode('utf8'),t_CompanyFacebookPage.encode('utf8'),t_CompanyPhoneNumber.encode('utf8'),
                       t_LocationOfCompanyUser.encode('utf8'),t_BadgeContainerProperties.encode('utf8'),t_NumberOfReviews.encode('utf8'),t_TopText.encode('utf8')])
    return rtn

def main():
    global g_outputfile, g_statusfilename
    global g_old_item_no
    global g_isfilevalid
    global g_view_from, g_view_to

    ### Staus file
    try:
        ins = open( g_statusfilename, "r" )
        for line in ins:
            p = re.compile(r'item_no=(?P<param>\d+)')
            m = p.search( line.rstrip() )
            if m is not None and m.group('param') is not None:
                g_old_item_no = int(m.group('param'))
                g_isfilevalid = True
                print_to_log("Last position - you scraped by this position.")
                print_to_log("before view no: "+str(g_old_item_no))
    except:
        pass

    if g_isfilevalid == False:
    #already done or start from begin
        print_to_log("===============================================================================")
        print_to_log("<"+g_statusfilename+"> file stands for saving scraping staus. Don't touch this file!")
        print_to_log("Saving status into this file, scraper continues from the last position.")
        print_to_log("In the case when scraper is terminated unsuccessfully, scraper continues from the position in the next time.")
        var = raw_input("Are you going to start scraping from begin?(yes/no):")
    	if var.lower() != "yes" and var.lower() != "y":
            sys.exit()
        var = raw_input("Did you backup all xml file?(yes/no):")
    	if var.lower() != "yes" and var.lower() != "y":
            sys.exit()

        #remove all output files
        if os.path.exists(g_outputfile):
            os.remove(g_outputfile)

    #Start Crawler
    print_to_log("===================================================================================")
    print_to_log("scraping running...")

    if not os.path.exists(g_outputfile):
        with open(g_outputfile,'wb') as f:
            fdWriter = csv.writer(f)
            fdWriter.writerow(['View No','Page URL','Number Of Properties','Company Website','Company FacebookPage','Company PhoneNumber','Location Of Company/User','Badge Container Properties','Number Of Reviews','TopText'])
            print g_outputfile+" newly created!"

    item_idx = g_view_from
    loop_flag = True
    while item_idx <= g_view_to:
        if item_idx < g_old_item_no:
            #already crawled
            pass
        else:
            page_url = "http://www.flipkey.com/frontdesk/view/%s/" % (item_idx)
            loop_flag = process_one_page(page_url, item_idx)
        item_idx += 1

    #done successfully!
    print_to_log("===================================================================================")
    print_to_log("Congratulations! Scraping successfully finished!")
    print_to_log("===================================================================================")
    os.remove(g_statusfilename)

if __name__ == "__main__":
    #is being run directly
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"f:t:",["viewfrom=","viewto="])
    except getopt.GetoptError:
        print_to_log('invalid input arguments!')
        print_to_log('ex) flipkey_crawler.py -f 1 -t 114638')
        print_to_log('    flipkey_crawler.py --viewfrom 1 --viewto 114638')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f", "--viewfrom"):
            g_view_from = int(arg)
        if opt in ("-t", "--viewto"):
            g_view_to = int(arg)
    print_to_log('View No from is %s' % (g_view_from))
    print_to_log('View No to is %s' % (g_view_to))
    main()
    