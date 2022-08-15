import requests
import json
from bs4 import BeautifulSoup
import urlparse
import csv
import datetime

def run_scrap(part_number, manufacture):

    product = {}
    product['name'] = ""
    product['weight'] = ""
    product['image_url'] = ""
    product['direc_cross'] = ""
    product['application'] = ""
    product["depth"] = ""
    product["category"] =manufacture

    url = "https://catalog.donaldson.com/misc/ajax/typeAhead.jsp"

    base_url = "https://catalog.donaldson.com"

    querystring = {"q":part_number}

    headers = {
        'host': "catalog.donaldson.com",
        'connection': "keep-alive",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        'referer': "https://catalog.donaldson.com/",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-US,en;q=0.8,es;q=0.6",
        'cache-control': "no-cache",
        'postman-token': "02941941-f572-f458-65c1-7724efce384b"
        }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)

        url_load_json = json.loads(response.text)['records']

        if (len(url_load_json) != 0):
            # print "record length", len((url_load_json))
            result_url = url_load_json[0]

            if(str(result_url['url']).split("//")[0] == "https:"):

                product_url = result_url['url']
            else:
                product_url = base_url+result_url['url']

            print(product_url)

            response_new_url = requests.request("GET", product_url, headers = headers)

            # soapData = BeautifulSoup(response_new_url.content,"html.parser").encode('utf-8')
            soapData = BeautifulSoup(response_new_url.content, "html.parser")
            items_product = soapData.find_all("tr",{"class":"item h-product"})

            # there are much product manufacture find one -> SCANIA
            for item_product in items_product:
                find_brand = item_product.find_all("td",{"class":"p-brand"})

                # check apakah terdapat data atau tidak
                if(len(find_brand)!=0):
                    if (find_brand[0].contents[0] == manufacture): #temukan berdasarkan manufacture
                        # print find_brand.content
                        # find links suitable product

                        partAppData=[]

                        alterPart = []


                        product_link = base_url+item_product.find("a",{"class":"hidden-print underline value u-url"}).get('href')

                        print product_link

                        # masukkan product name donaldson yang ditemukan
                        product_donaldson_num =item_product.find_all("a",{"class":"hidden-print underline value u-url"})
                        if(len(product_donaldson_num)!=0):
                            alterPart.append(product_donaldson_num[0].contents[0])
                        #
                            print "alterpart",alterPart

                        response_detail_product = requests.request("GET",product_link, headers=headers)

                        soapDetailProduct = BeautifulSoup(response_detail_product.content,"html.parser")

                        # find name

                        find_header= soapDetailProduct.find("h2",{"class":"container-fluid hidden-md hidden-lg clear-marginTop fn"})
                        find_name = find_header.find("strong").contents[0]

                        name = str(find_name)

                        product['name'] = name
                        print name


                        #find image_url
                        find_img = soapDetailProduct.find("img",{"class":"u-photo"})

                        img_url = find_img.get('src')
                        #
                        print img_url
                        product['image_url'] = img_url

                        # find Alternate Part

                        find_alt = soapDetailProduct.find_all("td",{"class":"u-identifier"})

                        if(len(find_alt) != 0):

                            for alt in find_alt:

                                alterPart.append(alt.find("span",{"class":"visible-print-inline"}).contents[0])

                            print alterPart

                        # find length

                        dls = soapDetailProduct.find_all("dl",{"class":"dl-horizontal fluid"})

                        for dl in dls:
                            dts = dl.find_all("dt",{"class":"fixed-md text-left"})

                            for dt in dts:
                                length = repr(dt.contents[0]).replace("\\r","").replace("\\n","").replace("\\t","").replace("u'","").replace("'","")

                                if(length == "Length:"):
                                    product["depth"] = repr(dl.find("dd").contents[0]).replace("\\xa0"," ").replace("u'","").replace("\\r","").replace("\\n","").replace("\\t","").replace("'","")


                        else:
                            print "No Alter Part"

                        product['direc_cross'] = ",".join(alterPart)
                        # find product appplication

                        # need to parser url for get productID nad skuID from url

                        url_parsed = urlparse.urlparse(product_link)

                        productId = urlparse.parse_qs(url_parsed.query)['productId'][0]
                        skuId = urlparse.parse_qs(url_parsed.query)['skuId'][0]


                        # print response_detail_product.content

                        urlapp = "https://catalog.donaldson.com/misc/ajax/loadingProductApplicationParts.jsp"

                        queryapp = {"productId": productId, "skuId": skuId}

                        headersapp = {
                            'x-requested-with': "XMLHttpRequest",
                            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
                        }

                        response_product_application = requests.request("GET", urlapp, headers=headersapp, params=queryapp)

                        soapProApp = BeautifulSoup(response_product_application.content,"html.parser")

                        part_applications = soapProApp.find_all("tr")

                        if(len(part_applications)!=0):

                            for part_application in part_applications:

                                application = {}

                                if(len(part_application.find_all("td"))>1):

                                    equipment = part_application.find("td").contents[0]

                                    engine = part_application.find_all("td")[4].contents[0]

                                    engine_clean = repr(engine).replace("u'","").replace("\\r","").replace("\\n","").replace("\\t","").replace("'","")

                                    clean_equipment = str(equipment).replace('\r\n\t\t\t\t\t\t\t\t',"").replace('\r\n\t\t\t\t\t\t\t',"")

                                    application["vehicle_brand"] = clean_equipment
                                    application["models"] = engine_clean

                                    if(str(clean_equipment).split(' ')[0] != 'No'):
                                        partAppData.append(application)
                                    else:
                                        partAppData = ""
                                else:
                                    partAppData = ""
                            product['application'] = partAppData
                        else:
                            print "no part application"

                    else:
                        print "data found but no ",manufacture
                else:
                    print "no brand available"

        else:
            print "data not found"

    except:
        print "error bro"


    with open('donaldson.csv', 'a') as csvoutput:
        fieldnames = ['sku', 'slug', 'name', 'price', 'weight', 'height', 'width',
                      'depth', 'image_product', 'image_product_2', 'image_product_3', 'image_product_4',
                      'description', 'category', 'on_hand', 'backorderable', 'direct_cross_interchange',
                      'indirect_cross_interchange','application']

        writer = csv.DictWriter(csvoutput, fieldnames=fieldnames)
        # writer.writeheader()
        product_for_write = {}

        product_for_write['sku'] = part_number
        product_for_write['slug'] = ""
        product_for_write['name'] = product['name']
        product_for_write['price'] = ""
        product_for_write['weight'] =""
        product_for_write['height'] = ""
        product_for_write['width'] = ""
        product_for_write['depth'] = product["depth"]
        product_for_write['image_product'] = product['image_url']
        product_for_write['image_product_2'] = ""
        product_for_write['image_product_3'] = ""
        product_for_write['image_product_4'] = ""
        product_for_write['description'] = ""
        product_for_write['category'] = "Brand > "+product["category"]
        product_for_write['on_hand'] = ""
        product_for_write['backorderable'] = ""
        product_for_write['direct_cross_interchange'] = product['direc_cross']
        product_for_write['indirect_cross_interchange'] = ""
        product_for_write['application'] = product['application']

        writer.writerow(product_for_write)

with open('input_file.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    print datetime.datetime.now()
    for idx, row in enumerate(reader):
        print 'sequence', idx
        part_number = (row['part_number'])

        manufacture = (row['manufacture'])

        run_scrap(part_number, manufacture)
        print part_number
        print '--------------------------'
    print datetime.datetime.now()