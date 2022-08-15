import requests
from bs4 import BeautifulSoup
import csv
import datetime

class WabCo:

    def run(self, part_number, manufact):

        product = {}
        product["part_number"] = part_number
        product["name"] = ""
        product["category"] ="Brand >"+ manufact
        product["product_url"] = ""
        product["image_url"] = [" "," "," "," "]
        product["cross_reference"] =[]
        product["price"] = ""
        product["application"] = []
        max_page = 0

        req = requests.Session()
        url = "http://inform.wabco-auto.com/intl/en/informcr.php"
        manufacture = manufact
        querystring = {"keywords": str(part_number), "max": "10", "save": "1", "select_comp": "", "keywords_send": str(part_number),
                       "loose_send": "", "loose": ""}

        response = req.request("GET", url, params=querystring)

        soapData = BeautifulSoup(response.text, "html.parser")

        # per page
        p = soapData.find_all("p", {"align": "center"})

        if (len(p) != 0):
            aas = p[0].find_all("a")

            # request tiap page
            if (len(aas) != 0):
                max_page = aas[len(aas) - 2].contents[0]

            for i in range(0, int(max_page)):
                print "page", i + 1
                url = "http://inform.wabco-auto.com/intl/en/informcr.php"
                querystring["page"] = str(i + 1)
                response = req.request("GET", url, params=querystring)
                soapData = BeautifulSoup(response.text, "html.parser")

                product_s_c = self.find_suitable_company(soapData, manufacture)

                if(product_s_c):
                    print product_s_c["product_url"]
                    product["cross_reference"].append(product_s_c["product_code"])
                    product_f_url = self.parser_product_url(product_s_c["product_url"], product_s_c["product_code"])
                    product["name"] = (product_f_url["name"])
                    for idx,image in enumerate(product_f_url["image"]):
                        product["image_url"][idx] = image
                    for alternate in product_f_url["alternate"]:
                        product["cross_reference"].append(alternate)
                    for replace in product_f_url["replacement"]:
                        product["cross_reference"].append(replace)
                    product["price"] = product_f_url["price"]
                    for app in product_f_url["application"]:
                        product["application"].append(app)
                    break
                else:
                    print "not found in this page"
                # print len(trs)

        # jika hanya ada satu page
        else:
            product_s_c = self.find_suitable_company(soapData, manufacture)

            if(product_s_c):
                product["cross_reference"].append(product_s_c["product_code"])
                product_f_url = self.parser_product_url(product_s_c["product_url"], product_s_c["product_code"])
                for idx, image in enumerate(product_f_url["image"]):
                    product["image_url"][idx] = image
                product["name"] = product_f_url["name"]
                for alternate in product_f_url["alternate"]:
                    product["cross_reference"].append(alternate)
                for replace in product_f_url["replacement"]:
                    product["cross_reference"].append(replace)
                product["price"] = product_f_url["price"]
                for app in product_f_url["application"]:
                    product["application"].append(app)
            else:
                "not found"
        return product

    def find_suitable_company(self, soapData, manufacture):
        product = {}

        tables = soapData.find_all("table", {"cellpadding": "2"})
        trs = tables[0].find_all("tr")
        if(len(trs)!=0):
            for i in range(2, len(trs) - 2, 2):

                company = repr(trs[i].find_all("td")[2].contents[0]).replace("u'","").replace("'","").upper()

                print company
                if (company == manufacture):
                    linktoproduct = trs[i].find_all("td")[3].find("a").get("href")
                    cross_part_num = trs[i].find_all("td")[3].find("a").contents
                    product["product_url"] = "http://inform.wabco-auto.com/intl/en/" + linktoproduct
                    product["product_code"] = cross_part_num[0]
                    break
            return product

    def parser_product_url(self, url, cross_code):

        print url

        req_s = requests

        product = {}

        product["cross_reference"] = []

        product["image"] = []

        product["alternate"] = []

        product["price"] = ""

        product["replacement"] = []

        product["application"] = []

        product["name"] = ""

        response = req_s.get(url)

        soapData = BeautifulSoup(response.text, "html.parser")

        radio_buttons = soapData.find_all("input", {"type": "radio"})

        for radio in radio_buttons:

            category_code = radio.get("value")

            url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                cross_code).replace(" ", "+") + "&category="+str(category_code)
            req_ts = req_s.get(url)
            soapTs = BeautifulSoup(req_ts.content, "html.parser")

            product["name"] = self.get_product_name(soapTs, cross_code)

            # technical sheet
            if (int(category_code) == 18):

                url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                    cross_code).replace(" ", "+") + "&category=18"
                req_ts = req_s.get(url)
                soapTs = BeautifulSoup(req_ts.content, "html.parser")

                product["name"]= self.get_product_name(soapTs, cross_code)

                imgs = soapTs.find_all("img")

                for idx in range(2, len(imgs) - 1):
                    # print imgs[idx].get("src")
                    product["image"].append("http://inform.wabco-auto.com"+str(imgs[idx].get("src")))

            # alternate
            if(int(category_code) == 10):
                url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                    cross_code).replace(" ", "+") + "&category=10"
                req_ts = req_s.get(url)
                soapTs = BeautifulSoup(req_ts.content, "html.parser")

                product["name"] = self.get_product_name(soapTs, cross_code)

                table = soapTs.find_all("table")

                tds = table[len(table)-1].find_all("td")

                for td in tds:
                    if (td.contents[0] == "Alternative: "):
                       for alt in td.find_all("a"):
                           product["alternate"].append(alt.contents[0])

            # gross price
            if (int(category_code) == 11):
                url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                    cross_code).replace(" ", "+") + "&category=11"
                req_ts = req_s.get(url)
                soapTs = BeautifulSoup(req_ts.content, "html.parser")

                product["name"] = self.get_product_name(soapTs, cross_code)

                td = soapTs.find_all("td", {"class": "clsWh"})

                price = td[1].contents[0]

                product["price"] = repr(price).replace("\\xa0"," ")

            # replacement
            if (int(category_code) == 9):
                url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                    cross_code).replace(" ", "+") + "&category=9"
                req_ts = req_s.get(url)
                soapTs = BeautifulSoup(req_ts.content, "html.parser")

                product["name"] = self.get_product_name(soapTs, cross_code)


                tables = soapTs.find_all("table")

                for td in tables[len(tables)-1].find_all("td"):

                    if(td.contents[0] == "Replacement: "):
                        product["replacement"].append(td.find("a").contents[0])
        #     applied in vehicle 22
            if (int(category_code) == 22):

                url = "http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords=" + str(
                    cross_code).replace(" ", "+") + "&category=22"
                req_ts = req_s.get(url)
                soapTs = BeautifulSoup(req_ts.content, "html.parser")

                product["name"] = self.get_product_name(soapTs, cross_code)

                product["application"] = self.handle_page_application(req_s,soapTs, cross_code)



        return product

    def get_product_name(self,soapData,product_code):

        td = soapData.find("td",{"background":"/intl/images/gradientbwhorizon.jpg"}).contents[0]

        name = repr(td).replace("\\xa0","").replace("u'","").split(product_code)[0]

        print name

        return name

    def handle_page_application(self, req_s,soapData, cross_ref):

        applied_product = []
        buffer = [""]
        application = {}
        application["models"] = []
        application["vehicle_brand"] = ""

        p = soapData.find_all("p", {"align": "center"})
        counter = 0
        if (len(p) != 0):
            aas = p[0].find_all("a")

            # request tiap page
            if (len(aas) != 0):
                max_page = aas[len(aas) - 2].contents[0]

            for i in range(0, int(max_page)):
                print "page", i + 1

                url = "http://inform.wabco-auto.com/intl/en/inform.php?keywords="+str(cross_ref).replace(" ","")+"&category=22&save=1&max=10&page="+str(i+1)+"&select_lang="

                response = req_s.get(url)

                soapData = BeautifulSoup(response.text, "html.parser")

                tables = soapData.find_all("table")

                ass = tables[len(tables)-1].find_all("a")

                for j in range(0, len(ass)-1):

                    if(buffer[len(buffer)-1] == str(ass[j].contents[0]).split(" ")[0]):
                        application["models"].append(repr(ass[j].contents[0]).replace("u'", "").replace("'",""))
                    else:
                        if(counter > 0):
                            applied_product.append(application)
                        application = {}
                        application["vehicle_brand"] = str(ass[j].contents[0]).split(" ")[0]
                        application["models"] = []
                        application["models"].append(repr(ass[j].contents[0]).replace("u'","").replace("'",""))
                        buffer.append(application["vehicle_brand"])

                    if (i+1 == int(max_page) and j+1 == len(ass)-1):
                        applied_product.append(application)

                    counter=counter + 1
        else:
            url ="http://inform.wabco-auto.com/intl/en/inform.php?familyname=&save=1&max=10&spaces=1&keywords="+str(cross_ref).replace(" ","+")+"&category=22"
            response = req_s.get(url)

            soapData = BeautifulSoup(response.text, "html.parser")

            tables = soapData.find_all("table")

            ass = tables[len(tables) - 1].find_all("a")

            for j in range(0, len(ass)):

                if (buffer[len(buffer) - 1] == str(ass[j].contents[0]).split(" ")[0]):
                    application["models"].append(repr(ass[j].contents[0]).replace("u'", "").replace("'",""))
                else:
                    if (counter > 0):
                        applied_product.append(application)
                    application = {}
                    application["vehicle_brand"] = str(ass[j].contents[0]).split(" ")[0]
                    application["models"] = []
                    application["models"].append(repr(ass[j].contents[0]).replace("u'", "").replace("'", ""))
                    buffer.append(application["vehicle_brand"])
                if (j + 1 == len(ass) - 1):
                    applied_product.append(application)

                counter = counter + 1

        return applied_product

with open('input_file.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    print datetime.datetime.now()
    for idx, row in enumerate(reader):
        print 'sequence', idx
        part_number = (row['part_number'])

        manufacture = (row['manufacture'])
        wab_co =  WabCo()
        product_from = wab_co.run(part_number,manufacture)

        with open('wabco.csv', 'a') as csvoutput:
            fieldnames = ['sku', 'slug', 'name', 'price', 'weight', 'height', 'width',
                          'depth', 'image_product', 'image_product_2', 'image_product_3', 'image_product_4',
                          'description', 'category', 'on_hand', 'backorderable', 'direct_cross_interchange',
                          'indirect_cross_interchange', 'application']

            writer = csv.DictWriter(csvoutput, fieldnames=fieldnames)
            # writer.writeheader()
            product_for_write = {}

            product_for_write['sku'] = product_from["part_number"]
            product_for_write['slug'] = ""
            product_for_write['name'] = product_from['name']
            product_for_write['price'] = ""
            product_for_write['weight'] = ""
            product_for_write['height'] = ""
            product_for_write['width'] = ""
            product_for_write['depth'] = ""
            product_for_write['image_product'] = product_from['image_url'][0]
            product_for_write['image_product_2'] = product_from['image_url'][1]
            product_for_write['image_product_3'] = product_from['image_url'][2]
            product_for_write['image_product_4'] = product_from['image_url'][3]
            product_for_write['description'] = ""
            if(product_from["name"]):
                product_for_write['category'] = product_from["category"]
            product_for_write['on_hand'] = ""
            product_for_write['backorderable'] = ""
            if(len(product_from['cross_reference'])!=0):
                product_for_write['direct_cross_interchange'] = ",".join(product_from['cross_reference'])
            product_for_write['indirect_cross_interchange'] = ""
            if(len(product_from['application'])!=0):
                product_for_write['application'] = product_from['application']

            writer.writerow(product_for_write)


        print part_number
        print '--------------------------'

    print datetime.datetime.now()






