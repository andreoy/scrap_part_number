import requests
from bs4 import BeautifulSoup
import csv
import datetime

def run_scrap(part_number):

    product = {}
    product["gtin"] = []
    product["application"] = []
    product['direc_cross'] = []

    url = "https://partnerportal.dieseltechnic.com/modules/unitm/um_es_search/ajax/main_search.php"

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"k\"\r\n\r\n"+str(part_number)+"\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "926135cb-aebd-4bcf-6fb2-e1bae5ffef6b"
        }

    print part_number

    response = requests.request("POST", url, data=payload, headers=headers)
    soapData = BeautifulSoup(response.content,"html.parser",)

    url_target = soapData.find_all('a')

    if(len(url_target) == 0):

        print ' not found'

        product['name']= ""
        product['weight'] = ""
        product['image_url'] = ""
        product['direc_cross'] = ""
        product['application'] = ""
        product['gtin'] = ""
        product["application"] = ""
        product['category'] = ""

    else:
        print 'wait ...'

        url_target = url_target[0].get('href')

        res_target = requests.request("GET", url_target)

        # print url_target

        soapTargetPage = BeautifulSoup(res_target.content,"html.parser")

        container = soapTargetPage.find("div",{"id":"nxsInfoContainerMain"})

        product['name'] = container.find("h3").contents[0]

        # print name

        cross_reference = container.find_all("p",{"class":"not-margined-bottom is-biggerer is-blue is-bold"})

        replaces = container.find_all("p",{"class":"is-lighter"})
        if(len(replaces)!=0):
            if(len(replaces[0].contents)!=0):

                rep = repr(replaces[0].contents[0]).replace("\\xb7"," ").replace("'"," ").split(":")

                if(len(rep) >1):
                    product['direc_cross'].append(rep[1])
                    print rep

        product['direc_cross'].append(cross_reference[1].contents[0])

        product['image_url'] = container.find("img",{"class":"product-details__img"}).get("data-zoom-image")

        # print image_url

        product['category'] = container.find_all("div",{"class":"is-hidden-lg"})[1].find_all("p",{"class":"not-margined-bottom"})[1].contents[0]

        weight = container.find_all("div",{"class":"row product-detail__info-container print-visible"})[0].\
            find("p",{"class":"not-margined-bottom shipping_condition"}).contents[0]


        product['weight'] = repr(weight).replace('\u2009'," ").replace("'","").replace('u','')

        # print product['weight']

        gtins = container.find_all("div",{"class":"col-xs-6"})[5].find_all("p",{"class":"not-margined-bottom"})

        for idx, div in enumerate(gtins):

            product["gtin"].append(div.contents[0])

        tables = soapTargetPage.find("table",{"id":"details-table__table--kompakt"})

        if(len(tables)!= 0):

            app = {}
            trs = tables.find_all("tr")

            for tr in trs[1:]:
                if (len(tr.find_all("td")) != 0):
                    app["vehicle_brand"] = repr(tr.find_all("td")[0].contents[0]).replace("u'","").replace("'","")
                    app["models"] = repr(tr.find_all("td")[1].contents[0]).replace("u'","").replace("'","")

                    product["application"].append(app)

        print product["application"]

    with open('dieseltechnic.csv', 'a') as csvoutput:
        fieldnames = ['sku', 'slug', 'name', 'price', 'weight', 'height', 'width',
                      'depth', 'image_product', 'image_product_2', 'image_product_3', 'image_product_4',
                      'description', 'category', 'on_hand', 'backorderable', 'direct_cross_interchange',
                      'indirect_cross_interchange','application','gtin']

        writer = csv.DictWriter(csvoutput, fieldnames=fieldnames)
        # writer.writeheader()
        product_for_write = {}
        product_for_write['sku'] = part_number
        product_for_write['slug'] = ""
        product_for_write['name'] = product['name']
        product_for_write['price'] = ""
        product_for_write['weight'] = product['weight']
        product_for_write['height'] = ""
        product_for_write['width'] = ""
        product_for_write['depth'] = ""
        product_for_write['image_product'] = product['image_url']
        product_for_write['image_product_2'] = ""
        product_for_write['image_product_3'] = ""
        product_for_write['image_product_4'] = ""
        product_for_write['description'] = ""
        product_for_write['category'] = "Brand > SCANIA"
        product_for_write['on_hand'] = ""
        product_for_write['backorderable'] = ""
        product_for_write['direct_cross_interchange'] = ",".join(product['direc_cross'])
        product_for_write['indirect_cross_interchange'] = ""
        product_for_write['application'] = product['application']
        product_for_write['gtin'] = ",".join(product['gtin'])

        writer.writerow(product_for_write)

with open('input_file.csv') as csvfile:
    reader = csv.DictReader(csvfile)

    print datetime.datetime.now()
    for idx,row in enumerate(reader):

        print 'sequence', idx
        part_number = (row['part_number'])
        try:
            run_scrap(part_number)
        except:
            print "error"
            pass
        print '--------------------------'

    print datetime.datetime.now()