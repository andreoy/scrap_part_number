import logging
import requests
from bs4 import BeautifulSoup
import csv
import datetime

# logging.basicConfig(level = logging.DEBUG)

def scrapProductUrl(url):

    product = {}
    product["name"] = ""
    product["image_url"] = ""
    product["direc_cross"] = []
    product["application"] = ""
    product["dtin"] = ""

    newSession = requests.Session()

    print "Request suitable Man Product Page"

    r = newSession.get(url)
    soapData = BeautifulSoup(r.content, "html.parser")
    viewStatePage = soapData.find("input", {"name": "javax.faces.ViewState"}).get("value")
    image_link = str(soapData.find("img", {"class": "detailImage"}).get("src")).replace("022","001")
    name = soapData.find("span", {"id": "productDetail:productName"}).contents[0]
    code = repr(soapData.find("h1",{"class":"m-all s-all t-all d-all cf borderBottom"}).contents[0]).replace("\\n\\t'","").replace("u'","")

    stin = soapData.find_all("span",{"class":"m-all s-1of2 t-3of5 d-2of3 last cf"})

    product["dtin"] = repr(stin[1].contents[0]).replace("u'","").replace("\\n","").replace("\\t","").replace("'","")

    product["direc_cross"].append(code)

    product["image_url"] = "https://catalog.mann-filter.com" + image_link

    product["name"] = name

    header_app = {

        "Host": "catalog.mann-filter.com",
        "Connection": "keep-alive",
        "Content-Length": "558",
        "Faces-Request": "partial/ajax",
        "Origin": "https://catalog.mann-filter.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
        "Referer": "https://catalog.mann-filter.com/EU/eng/catalog/MANN-FILTER%20Katalog%20Europa/Air%20Filter/C%2030%20850~7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8,es;q=0.6",
        "Cookie": "JSESSIONID=" + r.cookies['JSESSIONID'] + "; anonymousid=" + r.cookies[
            'anonymousid'] + "; MannHummelSSL=" + r.cookies['MannHummelSSL']
    }

    ################## application ##########

    payload_app = "&".join([
        "productDetail=productDetail&productDetail:productDetailTabPanel-value=productDetail:productDetailUsageTab",
        "javax.faces.ViewState=" + viewStatePage,
        "javax.faces.source=productDetail:productDetailUsageTab",
        "javax.faces.partial.execute=productDetail:productDetailUsageTab @component",
        "javax.faces.partial.render=@component",
        "org.richfaces.ajax.component=productDetail:productDetailUsageTab",
        "productDetail:productDetailUsageTab=productDetail:productDetailUsageTab",
        "rfExt=null",
        "AJAX:EVENTS_COUNT=1",
        "javax.faces.partial.ajax=true"])

    print "Request App tab"
    newSession.headers.update(header_app)
    r_app = newSession.post(url, data=payload_app)

    soapAppTab = BeautifulSoup(r_app.content, "lxml")
    #
    spans_r_app = soapAppTab.find_all("span", {"class": "label_lv1"})

    j_idt_detail_app = soapAppTab.find_all("span",{"style":"display: none;"})[0].get("id")

    print j_idt_detail_app

    app_mans = []
    product["application"] = []

    for span_r_app in spans_r_app:
        app_mans.append(span_r_app.contents[0])

    for app_man in app_mans:

        print app_man
        payload_apps_detail = "&".join(["productDetail=productDetail",
                                        "productDetail:productDetailTabPanel-value=productDetail:productDetailUsageTab",
                                        "javax.faces.ViewState=" + viewStatePage,
                                        "javax.faces.source="+j_idt_detail_app,
                                        "javax.faces.partial.execute="+j_idt_detail_app+" @component",
                                        "javax.faces.partial.render=@component",
                                        "name=" + app_man,
                                        "org.richfaces.ajax.component="+j_idt_detail_app,
                                        j_idt_detail_app+"="+j_idt_detail_app,
                                        "rfExt=null",
                                        "AJAX:EVENTS_COUNT=1",
                                        "javax.faces.partial.ajax=true"
                                        ])

        r_cross_detail = newSession.post(url, data=payload_apps_detail)

        soapDetailApp = BeautifulSoup(r_cross_detail.text, "lxml")

        spanApps = soapDetailApp.find_all("span", {"class": "label_lv2"})

        detailApp = []

        for spanApp in spanApps:
            detailApp.append(repr(spanApp.contents[0]).replace("u'","").replace("'",""))
        application = {}
        application["vehicle_brand"] = repr(app_man).replace("u'","").replace("'","")
        application["models"] = ",".join(detailApp)

        product["application"].append(application)


    ############### cross reference #########################
    payload_cross = "&".join(["productDetail=productDetail",
                              "productDetail:productDetailTabPanel-value=productDetail:productDetailCompareTab",
                              "javax.faces.ViewState=" + viewStatePage,
                              "javax.faces.source=productDetail:productDetailCompareTab",
                              "javax.faces.partial.execute=productDetail:productDetailCompareTab @component",
                              "javax.faces.partial.render=@component",
                              "org.richfaces.ajax.component=productDetail:productDetailCompareTab",
                              "productDetail:productDetailCompareTab=productDetail:productDetailCompareTab",
                              "rfExt=null",
                              "AJAX:EVENTS_COUNT=1",
                              "javax.faces.partial.ajax=true"])

    print "Request cross ref tab"
    r_cross = newSession.post(url, data=payload_cross)

    soapCrossTab = BeautifulSoup(r_cross.content, "lxml")

    span_jid = soapCrossTab.find_all("span", {"style": "display: none;"})[0].get("id")

    spans_r_cross = soapCrossTab.find_all("span", {"class": "label_lv1"})

    for spanCross in spans_r_cross:
        manufacture_cross = spanCross.contents[0]

        payload_cross_detail = "&".join(["productDetail=productDetail",
                                         "productDetail:productDetailTabPanel-value=productDetail:productDetailCompareTab",
                                         "javax.faces.ViewState=" + viewStatePage,
                                         "javax.faces.source=" + str(span_jid),
                                         "javax.faces.partial.execute=" + str(span_jid) + " @component",
                                         "javax.faces.partial.render=@component",
                                         "name=" + str(spanCross.contents[0]),
                                         "org.richfaces.ajax.component=" + str(span_jid),
                                         str(span_jid) + "=" + str(span_jid),
                                         "rfExt=null",
                                         "AJAX:EVENTS_COUNT=1",
                                         "javax.faces.partial.ajax=true"
                                         ])

        print "request code each manufacture"

        r_cross_detail = newSession.post(url, data=payload_cross_detail)

        soapCrossDetail = BeautifulSoup(r_cross_detail.content, "lxml")

        uls_basic = soapCrossDetail.find_all("ul", {"class": "basic_list"})
        # cross_code = []

        if (len(uls_basic) != 0):

            for ul_basic in uls_basic[0].find_all("li"):
                cross_code = ul_basic.contents[0]

                product["direc_cross"].append(cross_code)

    return product

def scrapManFilter(partnumber,manufacture):
    product_information = {}
    product_information["name"] = ""
    product_information["image_url"] = ""
    product_information["direc_cross"] = []
    product_information["application"] = ""
    product_information["dtin"] = ""

    headers = {
         "Upgrade-Insecure-Requests":"1",
         "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36"
    }

    s = requests.Session()
    s.headers.update(headers)
    print ("Request main page")
    r = s.get("https://catalog.mann-filter.com/EU/eng/oenumbers")

    soapData = BeautifulSoup(r.text,"html.parser")

    soapViewState = soapData.find_all("input",{"name":"javax.faces.ViewState"})

    if(len(soapViewState) != 0):

        viewState = soapViewState[0].get("value")

    else:
        print "No ViewState"
    j_idt = soapData.find("form",{"id":"autocompleteOEsearch:autocompleteOEsearch"}).find("span",{"style":"display: none;"}).get("id")

    # print j_idt

    cookies_response = r.cookies
    JSESSIONID = cookies_response['JSESSIONID']
    MannHummelSSL = cookies_response['MannHummelSSL']
    anonymousid = cookies_response['anonymousid']
    #
    #
    # print "Headers[Request]",(s.headers)
    # print "Headers[Response]",(r.headers)
    partNumber = partnumber
    manufacture_comparition = manufacture
    payload = "autocompleteOEsearch%3AautocompleteOEsearch=autocompleteOEsearch:autocompleteOEsearch" \
              "&autocompleteOEsearch:autocompleteOEsearch:searchQueryValue="+str(partNumber)+"" \
              "&autocompleteOEsearch:autocompleteOEsearch:searchQueryInput="+str(partNumber)+"" \
              "&javax.faces.ViewState="+viewState+"&javax.faces.source="+j_idt+"" \
              "&javax.faces.partial.execute="+j_idt+" @component" \
              "&javax.faces.partial.render=@component&searchQuery="+str(partNumber)+"" \
              "&org.richfaces.ajax.component="+j_idt+"&"+j_idt+"="+j_idt+"" \
              "&rfExt=null&AJAX:EVENTS_COUNT=1&javax.faces.partial.ajax=true"

    headers_search = {
        "Host": "catalog.mann-filter.com",
        "Connection": "keep-alive",
        "Content-Length": "781",
        "Faces-Request": "partial/ajax",
        "Origin": "https://catalog.mann-filter.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept": "*/*",
        "Referer": "https://catalog.mann-filter.com/EU/eng/oenumbers",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.8,es;q=0.6",
        "Cookie": "anonymousid="+anonymousid+"; JSESSIONID="+JSESSIONID+"; MannHummelSSL="+MannHummelSSL
    }

    s.headers.update(headers_search)

    # print "Headers[Requests]",(s.headers)
    print "Request partNumber"
    r = s.post("https://catalog.mann-filter.com/EU/eng/oenumbers",data=payload )
    # print "Headers[Response]", (r.headers)

    crcrs = r.headers['Set-Cookie']


    # print crcrs, r.cookies

    soapDataRealPage = BeautifulSoup(r.text,"html.parser")

    redirect_url = soapDataRealPage.find("redirect").get("url")

    print redirect_url

    headers_page = {

        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br",
        "Accept-Language":"en-US,en;q=0.8,es;q=0.6",
        "Connection":"keep-alive",
        "Cookie":"anonymousid="+anonymousid+"; MannHummelSSL="+MannHummelSSL+"; JSESSIONID="+JSESSIONID+"; csfcfc="+crcrs,
        "Host":"catalog.mann-filter.com",
        "Referer":"https://catalog.mann-filter.com/EU/eng/oenumbers",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "Upgrade-Insecure-Requests": "1"
    }

    print "Request redirect search URL"

    # s_new = requests.Session()
    s = requests.Session()
    s.headers.update(headers_page)
    url_page ="https://catalog.mann-filter.com"+redirect_url
    # r_r = s.get(url_page, headers = headers_page)
    r_r = s.get(url_page)

    print url_page
    print r_r.content

    # ======================================================================================================================
    # check there is data if true go to last get last number

    soapGetData = BeautifulSoup(r_r.text,"html.parser")

    # check if there is data
    table_Paging = soapGetData.find_all("div",{"class":"basic_pagingContent"})

    # update view State
    viewState_real_url = soapGetData.find("input",{"name":"javax.faces.ViewState"}).get("value")

    # print viewState_real_url

    if(len (table_Paging) == 0):
        print "No data Found"
        # make all data null
        # continue next data

    else:

        btns_page = soapGetData.find_all("a",{"class":"rf-ds-nmb-btn"})

        if (len(btns_page) == 0):
            print "there no page button"

            rows = soapGetData.find_all("div",{"class":"row"})

            for row in rows:
                row_data = row.find("div",{"class":"column compare_mannFilter"}).find_all("a")

                if(len(row_data)):
                    brand= row.find("div",{"class":"column compare_brand"}).find("div").contents[0]
                    clean_brand = repr(brand).replace("\\n","").replace("\\t","").replace("u'","").replace("'","")
                    if(clean_brand == manufacture_comparition):
                        man_link = "https://catalog.mann-filter.com" + row_data[0].get("href")
                        product_information = scrapProductUrl(man_link)
                else:
                   "no link"

        else:
            headers_last_page_request = {
                "Host": "catalog.mann-filter.com",
                "Connection": "keep-alive",
                # "Content-Length": "678",
                "Faces-Request": "partial/ajax",
                "Origin": "https://catalog.mann-filter.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
                "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "*/*",
                "Referer":str(url_page),
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.8,es;q=0.6",
                "Cookie": "anonymousid=" + anonymousid + "; JSESSIONID=" + JSESSIONID + "; MannHummelSSL=" + MannHummelSSL
            }

            find_j_idt = soapGetData.find_all("span",{"class":"rf-ds"})

            j_idt_page = repr(find_j_idt[0].get("id")).split(":")[0].replace("u'","")

            # s_new.headers.update(headers_last_page_request)
            s.headers.update(headers_last_page_request)

            payload_last_page_request = "headerSearchForm:headerSearchForm=headerSearchForm:headerSearchForm" \
                                        "&headerSearchForm:headerSearchForm:searchQueryValue=" \
                                        "&headerSearchForm:headerSearchForm:searchQueryInput=Search catalog" \
                                        "&javax.faces.ViewState="+viewState_real_url+"" \
                                        "&javax.faces.source="+j_idt_page+":dataScroller" \
                                        "&javax.faces.partial.event=rich:datascroller:onscroll" \
                                        "&javax.faces.partial.execute="+j_idt_page+":dataScroller @component" \
                                        "&javax.faces.partial.render=@component&"+j_idt_page+":dataScroller:page=last" \
                                        "&org.richfaces.ajax.component="+j_idt_page+":dataScroller" \
                                        "&"+j_idt_page+":dataScroller="+j_idt_page+":dataScroller" \
                                        "&rfExt=null&AJAX:EVENTS_COUNT=1&javax.faces.partial.ajax=true"
            print "Request Last Page"
            # r_lp = s_new.post(url_page, data=payload_last_page_request)
            r_lp = s.post(url_page, data=payload_last_page_request)
            soapDataLastPage = BeautifulSoup(r_lp.text,"lxml")
            lastPage = soapDataLastPage.find_all("span")[1].contents[0]

            for i in range(int(lastPage), 0, -1):

                payload_for_page ="&".join(["headerSearchForm:headerSearchForm=headerSearchForm:headerSearchForm",
                                            "headerSearchForm:headerSearchForm:searchQueryValue=",
                                            "headerSearchForm:headerSearchForm:searchQueryInput=Search catalog",
                                            "javax.faces.ViewState="+viewState_real_url,
                                            "javax.faces.source="+j_idt_page+":dataScroller",
                                            "javax.faces.partial.event=rich:datascroller:onscroll",
                                            "javax.faces.partial.execute="+j_idt_page+":dataScroller @component",
                                            "javax.faces.partial.render=@component",
                                            str(j_idt_page)+":dataScroller:page="+str(i),
                                            "org.richfaces.ajax.component="+j_idt_page+":dataScroller",
                                            str(j_idt_page)+":dataScroller="+str(j_idt_page)+":dataScroller",
                                            "rfExt=null",
                                            "AJAX:EVENTS_COUNT=1",
                                            "javax.faces.partial.ajax=true"])

                print "Request for each page"
                # s_new.headers.update(headers_for_page)
                res_per_page = s.post(url_page, data=payload_for_page)

                # find suitable manufactur
                soapDataTabelResultSearch = BeautifulSoup(res_per_page.text,"lxml")

                manufactures = soapDataTabelResultSearch.find("update").contents

                rows=str(manufactures[1]).split('<div class="row">')

                for idx,row in enumerate(rows[1:]):

                    tandas = row.split('">')

                    manufacture_got= str(tandas[4].split("</div>")[0]).encode('utf-8')
                    manufacture_clean = repr(manufacture_got).replace("'","").replace("\\t","").replace("\\n","")

                    if (""+manufacture_comparition == ""+manufacture_clean):
                        print "FOUND !!!!!!"

                        available_MANN = row.split('<a href="')

                        if(len(available_MANN) > 1):

                            # man_product_code = available_MANN[1].split('">')[1].split("/a>")[0]
                            # man_product_code_clean = repr(man_product_code).replace("'","").replace("\\n","").replace("\\t","").replace("<","")

                            man_product_link = available_MANN[1].split('"')[0]

                            url = "https://catalog.mann-filter.com"+man_product_link

                            product_information = scrapProductUrl(url)


                        else:
                            print "not available"

        with open('man-filter.csv', 'a') as csvoutput:
            fieldnames = ['sku', 'slug', 'name', 'price', 'weight', 'height', 'width',
                          'depth', 'image_product', 'image_product_2', 'image_product_3', 'image_product_4',
                          'description', 'category', 'on_hand', 'backorderable', 'direct_cross_interchange',
                          'indirect_cross_interchange','application','dtin']

            writer = csv.DictWriter(csvoutput, fieldnames=fieldnames)
             # writer.writeheader()
            product_for_write = {}

            product_for_write['sku'] = part_number
            product_for_write['slug'] = ""
            product_for_write['name'] = product_information['name']
            product_for_write['price'] = ""
            product_for_write['weight'] =""
            product_for_write['height'] = ""
            product_for_write['width'] = ""
            product_for_write['depth'] = ""
            product_for_write['image_product'] = product_information['image_url']
            product_for_write['image_product_2'] = ""
            product_for_write['image_product_3'] = ""
            product_for_write['image_product_4'] = ""
            product_for_write['description'] = ""
            product_for_write['category'] = ""
            product_for_write['on_hand'] = ""
            product_for_write['backorderable'] = ""
            product_for_write['direct_cross_interchange'] = ",".join(product_information['direc_cross'])
            product_for_write['indirect_cross_interchange'] = ""
            product_for_write['application'] = product_information['application']
            product_for_write['dtin'] = product_information['dtin']
            writer.writerow(product_for_write)

with open('input_file.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    print datetime.datetime.now()
    for idx, row in enumerate(reader):
        print 'sequence', idx
        part_number = (row['part_number'])

        manufacture = (row['manufacture'])
        scrapManFilter(part_number, manufacture)
        print part_number
        print '--------------------------'
    print datetime.datetime.now()
