from Product import Product
import requests
from bs4 import BeautifulSoup
import csv
import datetime

class Scrapper:

    def __init__(self):

      self.main_url = 'http://www.kakapart.com'


    def find_by_product_info(self, product_link):

        product = Product()

        response = requests.request("GET", product_link)

        print product_link
        soapData = BeautifulSoup(response.content, "html.parser")

        # find application

        app = soapData.find_all("div",{"class":"model clearfix"})

        if(len(app)!=0):

            manuf = []
            as_manuf = app[0].find_all("ul",{"class":"make"})

            if (len(as_manuf)!=0):
                aaa = as_manuf[0].find_all("a")

                for a_manuf in aaa:
                    manuf.append(a_manuf.contents[0])

                series_con = app[0].find_all("div",{"class":"L_me"})

                Applications = []

                for idx,each_manuf in enumerate(manuf):
                    series = series_con[idx].find_all("li",{"class":"sFfea"})
                    series_man = []
                    for seri in series:
                        series_man.append(str(seri.contents).replace("[u","").replace("<span>"," ").replace("</span>"," ").replace("]","").replace("u'","").replace("'","").replace(", ",""))

                    application = {}

                    # print each_manuf

                    application["model"] = ",".join(series_man)
                    application["vehicle_brand"] = str(each_manuf)

                    Applications.append(application)

                product.application =  Applications

        product_mask = soapData.find('div', {'class': "prodpic FL"})

        if(product_mask):
            get_img = product_mask.find_all('img', {"class": "smallpic"})
            for idx, img in enumerate(get_img):
                if (img.get("img") != str("/images/nophoto_img.gif")):
                    product.image_product = img.get('img')

        get_desc = soapData.find_all('ul', {'class': 'oem-applicUl'})[0].find_all('p')
        description = ""
        for desc in get_desc[1:]:
            description = description + "\n" + repr(desc.contents[0]).replace("\uff1a"," ").replace("u'","").replace("'","")
            # print description

            # print desc.contents[0]
        product.description = description

        category = repr(get_desc[1].contents[0]).replace("\uff1a"," ").replace("u'","").replace("'","").replace("Brand ","")

        product.category = category


        # application = soapData.find("ul",{"class":"oem-applicUl"}).find("a",{"href":"javascript:;"}).contents[0]
        # product.application = application
        # cross interchange

        interchange_link = soapData.find_all('div', {'class': 'oem-replacePos'})[0].find('a').get('href')

        url_cross_change = self.main_url + interchange_link

        response_interchange = requests.request("GET", url_cross_change)

        soapInterChange = BeautifulSoup(response_interchange.content, "html.parser")
        intechanges = soapInterChange.find_all("tr", {"class": "os-row"})

        direc_cross_interchange = []
        indirec_cross_interchange = []

        for intechange in intechanges:
            detail_cross_interchange = intechange.find_all("td")

            if (detail_cross_interchange[2].contents[0] == 'Direct Cross Interchange'):
                direc_cross_interchange.append(detail_cross_interchange[1].contents[0])

            if (detail_cross_interchange[2].contents[0] == 'Indirect Cross Interchange'):
                indirec_cross_interchange.append(detail_cross_interchange[1].contents[0])

        product.direct_cross_interchange = direc_cross_interchange
        product.indirect_cross_interchange = indirec_cross_interchange



        return product

    def runScrapper(self):

        with open('input_file.csv') as csvfile:
            reader = csv.DictReader(csvfile)

            for idx, row in enumerate(reader):

                product = Product()

                part_number = (row['part_number'])


                # print 'process for product', part_number, 'wait...'

                try:
                    response = requests.request("GET", "http://www.kakapart.com/search/defaultsearch/" + part_number)
                except requests.exceptions.RequestException as e:  # This is the correct syntax
                    print e

                soupResponse = BeautifulSoup(response.content, "html.parser")

                get_all_brand = soupResponse.find_all('tr', {'style': "border-bottom: 1px dashed #DDDDDD;height:35px;"})

                if (len(get_all_brand) == 0):
                    print("Data not found")

                else:
                    for brand in get_all_brand:
                        dig_brand = brand.find_all('a')

                        brand_link = self.main_url + dig_brand[0].get('href')
                        brand_name = dig_brand[0].contents[0]
                        product_kode = dig_brand[1].contents[0]

                        # print brand_name
                        product_name_soap = brand.find_all('td')

                        if (brand_name == 'SCANIA' and  product_kode == part_number ):
                            product = self.find_by_product_info(brand_link)
                            if (len(product_name_soap) > 2):
                                product_name_soap_span = product_name_soap[2].find('span')
                                if (len(product_name_soap_span) != 0):
                                    product.name = product_name_soap_span.contents[0]

                product.sku = part_number

                with open('kakapart.csv', 'a') as csvoutput:
                    fieldnames = ['sku', 'slug', 'name', 'price', 'weight', 'height', 'width',
                                  'depth', 'image_product', 'image_product_2', 'image_product_3', 'image_product_4',
                                  'description', 'category', 'on_hand', 'backorderable', 'direct_cross_interchange',
                                  'indirect_cross_interchange','application']

                    writer = csv.DictWriter(csvoutput, fieldnames=fieldnames)

                    product_for_write = {}
                    product_for_write['sku'] = product.sku
                    product_for_write['slug'] = product.slug
                    product_for_write['name'] = product.name
                    product_for_write['price'] = product.price
                    product_for_write['weight'] = product.weight
                    product_for_write['height'] = product.height
                    product_for_write['width'] = product.width
                    product_for_write['depth'] = product.depth
                    product_for_write['image_product'] = product.image_product
                    product_for_write['image_product_2'] = product.image_product_2
                    product_for_write['image_product_3'] = product.image_product_3
                    product_for_write['image_product_4'] = product.image_product_4
                    product_for_write['description'] = product.description
                    product_for_write['category'] = product.category
                    product_for_write['on_hand'] = product.on_hand
                    product_for_write['backorderable'] = product.backorderable
                    product_for_write['direct_cross_interchange'] = ",".join(product.direct_cross_interchange).encode('utf-8').strip()
                    product_for_write['indirect_cross_interchange'] = ",".join(product.indirect_cross_interchange).encode('utf-8').strip()
                    product_for_write['application'] = product.application

                    writer.writerow(product_for_write)

                    print product_for_write
                # print 'process for product', part_number, 'queue', idx


print datetime.datetime.now()
scrapper = Scrapper()
scrapper.runScrapper()
print datetime.datetime.now()
