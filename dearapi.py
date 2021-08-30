import requests
from ratelimit import limits, sleep_and_retry
import decimal
import re

class dearapi:

    #private
    _headers = {}
    _accountid = ""
    _apikey = ""
    #public

    #methods

    def _url(self, path):
        return "https://inventory.dearsystems.com/ExternalApi/v2/" + path


    @sleep_and_retry
    @limits(calls=30, period=60)
    def check_limit(self):
        #acts as global ratelimit checker
        return

    def loadCredentials(self):
        with open('credentials.txt', 'r') as reader:
            credlist = [line.rstrip() for line in reader]
            if(len(credlist) < 2):
                print("Error loading credentials")
                sys.exit()
                
            self._accountid = credlist[0]
            self._apikey = credlist[1]

            self._headers = {"api-auth-accountid" : self._accountid, "api-auth-applicationkey" : self._apikey}

            

    def getSkusFromLines(self, lines):
        skus = []
        for line in lines:
            for i in range(0,int(line['Quantity'])):
                skus.append(line['SKU'])
        return skus

    # page is number
    def getAvailabilityAllFullFace(self, page):
        self.check_limit()
        req = requests.get(self._url("ref/productavailability"), params={'Category':'DOT Full Face Helmet', 'Page' : page},  headers=self._headers)
        return req.json()


    @sleep_and_retry
    @limits(calls=40, period=60)
    def searchSalesByOrderNum(self, orderNum):
        self.check_limit()
        return requests.get(self._url("/saleList/"), params={'Search' : orderNum}, headers=self._headers)

    @sleep_and_retry
    @limits(calls=40, period=60)
    def undoSale(self, sale_id):
        self.check_limit()
        return requests.delete(self._url("/sale/"), params={'ID' : sale_id}, headers=self._headers)

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getLinesFromSaleOrder(self, sale_id):
        self.check_limit()
        return requests.get(self._url("/sale/"), params={'ID' : sale_id}, headers=self._headers).json()['Order']['Lines']

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getSaleOrder(self, sale_id):
        self.check_limit()
        return requests.get(self._url("/sale/"), params={'ID' : sale_id}, headers=self._headers).json()['Order']

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getSale(self, sale_id):
        self.check_limit()
        return requests.get(self._url("/sale/"), params={'ID' : sale_id}, headers=self._headers).json()

    @sleep_and_retry
    @limits(calls=40, period=60)
    def putSale(self, order):
        self.check_limit()
        return requests.post(self._url("/sale/"), json=order, headers=self._headers)

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postOrder(self, order):
        self.check_limit()
        return requests.post(self._url("/sale/order/"), json=order, headers=self._headers)

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postQuote(self, quote):
        self.check_limit()
        return requests.post(self._url("/sale/quote/"), json=quote, headers=self._headers)


    
    @sleep_and_retry
    @limits(calls=40, period=60)
    def getProduct(self, sku):
        self.check_limit()
        req = requests.get(self._url("/product/"), params={'Sku' : sku}, headers=self._headers).json()['Products']
        if len(req) == 0:
            return None
        return req[0]

    
    @sleep_and_retry
    @limits(calls=40, period=60)
    def getAvailabilityList(self, sku):
        self.check_limit()
        guid = self.getProduct(sku)['ID']
        req = requests.get(self._url("ref/productavailability"), params={'ID' : guid, 'Sku' : sku, 'Location' : 'Vancouver - Default'}, headers=self._headers) #warehouse is "Vancouver - Default"
        ava = req.json()['ProductAvailabilityList']
        return ava

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getAvailableInBin(self, helm_bin):
        self.check_limit()
        req = requests.get(self._url("ref/productavailability"), params={'Location' : helm_bin}, headers=self._headers) #warehouse is "Vancouver - Default"
        print(req.status_code)
        print(req.text)
        ava = req.json()['ProductAvailabilityList']
        return ava

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getAvailability(self, sku):
        self.check_limit()
        prod = self.getProduct(sku)
        if prod == None:
            return 0
        guid = prod['ID']
        req = requests.get(self._url("ref/productavailability"), params={'ID' : guid, 'Sku' : sku, 'Location' : 'Vancouver'}, headers=self._headers) #warehouse is "Vancouver - Default"
        if req.status_code != 200:
            print("Error: getAvailability: " + sku + " is unable to process http request!" )
            print(req.status_code)
            print(req.text)
        ava = req.json()['ProductAvailabilityList']
        objlist = []
        for jsobj in ava:
            if jsobj['Location'] == 'Vancouver - Default':
                objlist.append(jsobj['Available'])
        return sum(objlist)


    @sleep_and_retry
    @limits(calls=40, period=60)
    def getAvailabilityInfo(self, sku):
        self.check_limit()
        prod = self.getProduct(sku)
        if prod == None:
            return 0
        guid = prod['ID']
        req = requests.get(self._url("ref/productavailability"), params={'ID' : guid, 'Sku' : sku, 'Location' : 'Vancouver'}, headers=self._headers) #warehouse is "Vancouver - Default"
        if req.status_code != 200:
            print("Error: getAvailability: " + sku + " is unable to process http request!" )
            print(req.status_code)
            print(req.text)
        ava = req.json()['ProductAvailabilityList']
        objlist = []
        return ava

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getAllAvailability(self, sku):
        self.check_limit()
        guid = self.getProduct(sku)['ID']
        req = requests.get(self._url("ref/productavailability"), params={'ID' : guid, 'Sku' : sku, 'Location' : 'Vancouver'}, headers=self._headers) #warehouse is "Vancouver - Default"
        if req.status_code != 200:
            print("Error: getAvailability: " + sku + " is unable to process http request!" )
            print(req.status_code)
            print(req.text)
        ava = req.json()['ProductAvailabilityList']
        objlist = []
        for jsobj in ava:
            if jsobj['Location'] == 'Vancouver - Default':
                objlist.append(jsobj['Available'])
        return objlist

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postStockAdjustment(self, jsonVar):
        self.check_limit()
        post = requests.post(self._url("/stockadjustment/"), json=jsonVar, headers=self._headers)
        return post

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postQuoteItems(self, saleid, items):
        self.check_limit()
        quote = requests.get(self._url("/sale/"), params={'ID' : saleid}, headers=self._headers).json()['Order']
        # break up sku here, make list of items

        cents = decimal.Decimal('.01')

        totalAdditionalCharges = decimal.Decimal(0)
        totalAdditionalTaxes = decimal.Decimal(0)
        for add in quote['AdditionalCharges']:
            totalAdditionalCharges += decimal.Decimal((add['Total'])).quantize(cents,decimal.ROUND_HALF_UP) # - add['Tax']
            totalAdditionalTaxes += decimal.Decimal(add['Tax']).quantize(cents,decimal.ROUND_HALF_UP)

        totalBeforeTax = decimal.Decimal(quote['TotalBeforeTax']).quantize(cents,decimal.ROUND_HALF_UP) - decimal.Decimal(totalAdditionalCharges).quantize(cents,decimal.ROUND_HALF_UP)
        tax = decimal.Decimal(quote['Tax']).quantize(cents,decimal.ROUND_HALF_UP) - totalAdditionalTaxes

        #print(totalBeforeTax)
        #print(totalAdditionalCharges)
        #print(totalAdditionalTaxes)

        costList = self.distributeCost(totalBeforeTax,tax,items)

        #print(costList)

        if(len(quote['Lines']) == 0):
            print("Error: Empty order lines")
            print(saleid)
            return


        discount = round(quote['Lines'][0]['Discount'],2)
        taxRule = quote['Lines'][0]['TaxRule'] #TAX RULE LINE, HAVE TO MODIFY
        comment = quote['Lines'][0]['Comment']

        lines = []
        index = 0
        for sku in items:
            #print(sku)
            prod= self.getProduct(sku)

            line = {'ProductID' : prod['ID'], 'SKU' : sku, 'Name' : prod['Name'], 'Quantity' : 1, 'Price' : decimal.Decimal(costList[index][1]).quantize(cents,decimal.ROUND_HALF_UP), 'Discount':discount,  "Tax" : decimal.Decimal(costList[index][2]).quantize(cents,decimal.ROUND_HALF_UP), 'AverageCost' : prod['AverageCost'], 'TaxRule' : taxRule, 'Comment' : comment, 'Total' : decimal.Decimal(costList[index][1]).quantize(cents,decimal.ROUND_HALF_UP)}
            lines.append(line);
            index+=1

        #print(lines)
        quote['SaleID'] = saleid
        quote['Lines'] = lines
        quote['Status'] = "AUTHORISED"

        quote['AutoPickPackShipMode'] = 'AUTOPICK'

        print("posting" + saleid + "...")

        post = self.postOrder(quote)

        print("posted")

        return post

    
    @sleep_and_retry
    @limits(calls=40, period=60)
    def postBackorderQuoteItems(self, saleid, items):
        self.check_limit()
        sale = requests.get(self._url("/sale/"), params={'ID' : saleid}, headers=self._headers).json()
        quote = sale['Order']
        # break up sku here, make list of items

        sale['Status'] = "BACKORDERED"
        
        
        cents = decimal.Decimal('.01')

        totalAdditionalCharges = decimal.Decimal(0)
        totalAdditionalTaxes = decimal.Decimal(0)
        for add in quote['AdditionalCharges']:
            totalAdditionalCharges += decimal.Decimal((add['Total'])).quantize(cents,decimal.ROUND_HALF_UP) # - add['Tax']
            totalAdditionalTaxes += decimal.Decimal(add['Tax']).quantize(cents,decimal.ROUND_HALF_UP)

        totalBeforeTax = decimal.Decimal(quote['TotalBeforeTax']).quantize(cents,decimal.ROUND_HALF_UP) - decimal.Decimal(totalAdditionalCharges).quantize(cents,decimal.ROUND_HALF_UP)
        tax = decimal.Decimal(quote['Tax']).quantize(cents,decimal.ROUND_HALF_UP) - totalAdditionalTaxes

        #print(totalBeforeTax)
        #print(totalAdditionalCharges)
        #print(totalAdditionalTaxes)

        costList = self.distributeCost(totalBeforeTax,tax,items)

        #print(costList)

        if(len(quote['Lines']) == 0):
            print("Error: Empty order lines")
            print(saleid)
            return


        discount = round(quote['Lines'][0]['Discount'],2)
        taxRule = quote['Lines'][0]['TaxRule']
        comment = quote['Lines'][0]['Comment']

        lines = []
        index = 0
        for sku in items:
            #print(sku)
            prod= self.getProduct(sku)

            line = {'ProductID' : prod['ID'], 'SKU' : sku, 'Name' : prod['Name'], 'Quantity' : 1, 'Price' : decimal.Decimal(costList[index][1]).quantize(cents,decimal.ROUND_HALF_UP), 'Discount':discount,  "Tax" : decimal.Decimal(costList[index][2]).quantize(cents,decimal.ROUND_HALF_UP), 'AverageCost' : prod['AverageCost'], 'TaxRule' : taxRule, 'Comment' : comment, 'Total' : decimal.Decimal(costList[index][1]).quantize(cents,decimal.ROUND_HALF_UP)}
            lines.append(line);
            index+=1

        #print(lines)
        quote['SaleID'] = saleid
        quote['Lines'] = lines

        quote['AutoPickPackShipMode'] = 'AUTOPICK'


        print(quote['Status'])
        
        print("posting order" + saleid + "...")

        sale['Order'] = quote

        post = self.putSale(sale)

        print(post.status_code)
        print(post.text)

        print("posted")

        if(post.status_code == 200):
            pass

        return post

    @sleep_and_retry
    @limits(calls=40, period=60)
    def getTask(self, saleid):
        self.check_limit()
        # get sale fulfillment from saleid
        # post autopick

        full = requests.get(self._url("/sale/fulfilment"), params={'SaleID' : saleid}, headers=self._headers).json()
        task = full['Fulfilments'][0]['TaskID']
        return task
        
    @sleep_and_retry
    @limits(calls=40, period=60)
    def enableAutoPick(self, saleid):
        self.check_limit()
        # get sale fulfillment from saleid
        # post autopick
        task = self.getTask(saleid)
        jsonVar = {'TaskID' : task, 'AutoPickMode' : 'AUTOPICK' }
        post = requests.post(self._url("/sale/fulfilment/pick"), json=jsonVar, headers=self._headers)


    @sleep_and_retry
    @limits(calls=40, period=60)
    def getInvoice(self, saleid):
        self.check_limit()
        invoice = requests.get(self._url("/sale/invoice"), params={'SaleID' : saleid}, headers=self._headers).json()['Invoices'][0]
        return invoice
        
    @sleep_and_retry
    @limits(calls=40, period=60)
    def authorizeInvoice(self, saleid):
        self.check_limit()

        invoice = self.getInvoice(saleid)
        print(invoice)
        print('-------')
        invoice['Status'] = "AUTHORISED"
        invoice['SaleID'] = saleid
        post = requests.post(self._url("/sale/invoice"), json=invoice, headers=self._headers)
        if(post.status_code != 200):
            print("Error authorizing invoice for saleid " + saleid)
        else:
            print(post.json())

        
        
        
    

    def distributeCost(self, totalBeforeTax, tax, items):
        cents = decimal.Decimal('.01')
        helmIndices = []
        index = 0
        for sku in items:
            if (re.search("(989|988|601|580|707|801|888)(-F70)*-((([0-9])*[0-9])*[0-9])", sku) != None):
                helmIndices.append(index)
            index += 1
        #want helmets to account for 3/4 of cost

        print("Helm #: " + str(len(helmIndices)))

        helmCost = 0
        helmTax = 0
        accCost = 0
        accTax = 0


        if(len(items) == 0):
            return

        #check for divide by zero
        if len(helmIndices) == 0:
            accCost = decimal.Decimal(totalBeforeTax*decimal.Decimal((1/(len(items) - len(helmIndices))))).quantize(cents,decimal.ROUND_HALF_UP)
            accTax = decimal.Decimal(decimal.Decimal((1/4))*tax*decimal.Decimal((1/(len(items) - len(helmIndices))))).quantize(cents,decimal.ROUND_HALF_UP)
        else:

            helmCost = decimal.Decimal(decimal.Decimal((3/4))*totalBeforeTax*decimal.Decimal((1/(len(helmIndices))))).quantize(cents,decimal.ROUND_HALF_UP)
            helmTax = decimal.Decimal(decimal.Decimal((3/4))*tax*decimal.Decimal((1/(len(helmIndices)))))

            if len(helmIndices) != len(items):
                accCost = decimal.Decimal(decimal.Decimal((1/4))*totalBeforeTax*decimal.Decimal((1/(len(items) - len(helmIndices))))).quantize(cents,decimal.ROUND_HALF_UP)
                accTax = decimal.Decimal(decimal.Decimal((1/4))*tax*decimal.Decimal((1/(len(items) - len(helmIndices))))).quantize(cents,decimal.ROUND_HALF_UP)

        priceList = []

        for i in range(0,len(items)):
            if(i in helmIndices):
                priceList.append((items[i],helmCost,helmTax))
            else:
                priceList.append((items[i],accCost,accTax))
            firstTotalNT = 0
            firstTotalT = 0
            for item in priceList:
                firstTotalNT += item[1]
                firstTotalT += item[2]
            diffNT = totalBeforeTax - firstTotalNT
            if(len(priceList) > 0):
                oldTup = priceList[0]
                newTup = (oldTup[0], oldTup[1] + diffNT, oldTup[2])
                priceList[0] = newTup

            diffT = tax - firstTotalT
            if(len(priceList) > 0):
                oldTup = priceList[0]
                newTup = (oldTup[0], oldTup[1], oldTup[2] + diffT)
                priceList[0] = newTup

        return priceList

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postNewItems(self, saleid, items):
        self.check_limit()
        if(self.postQuoteItems(saleid, items).status_code != 200):
            print("Error posting ORDER - aborting")
            return False

    @sleep_and_retry
    @limits(calls=40, period=60)
    def postNewBackorderItems(self, saleid, items):
        self.check_limit()
        if(self.postBackorderQuoteItems(saleid, items).status_code != 200):
            print("Error posting backordered ORDER - aborting")
            return False


    def getAllProducts(self, page):
        self.check_limit()
        req = requests.get(self._url("/product/"), params={'Page' : page}, headers=self._headers).json()
        return req
