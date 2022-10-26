# Mouser API

We cannot search part by features like in the Mouser site.

* https://www.mouser.fr/api-hub
* https://www.mouser.fr/MyMouser/MouserSearchApplication.aspx

* https://www.mouser.fr/api-search
* https://api.mouser.com/api/docs/ui/index

Features
* Search by Keyword Method
* Search by Part Number Method
* Up to 50 results returned per call
* Up to 30 calls per minute
* Up to 1,000 calls per day

What data is available?
* Number of Results Found
* Mouser Part Number
* Manufacturer Part Number
* Manufacturer Name
* Availability
* Data Sheet URL
* Part Description
* Image URL
* Product Category
* Packaging
* Product Compliance
* Lifecycle Status
* RoHS Status
* Reeling Availability
* Minimum Order Quantity
* Order Quantity Multiples
* Lead Time
* Suggested Replacement(s)
* Product Detail Page URL
* Pricing Information (up to 4 price breaks)
* Standard Pack Quantity

```
fabrice.salvaire@orange.fr
Your API Key: 21a461f4-0dd9-47b5-a082-0a7426d51243
Assigned To: fabrice salvaire
For: test
```

Read **models** to get full documentation

```
curl -X POST "https://api.mouser.com/api/v1/search/keyword?apiKey=21a461f4-0dd9-47b5-a082-0a7426d51243" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"SearchByKeywordRequest\": {    \"keyword\": \"avr\"  }}"

curl -X POST "https://api.mouser.com/api/v1/search/partnumber?apiKey=21a461f4-0dd9-47b5-a082-0a7426d51243" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"SearchByPartRequest\": {    \"mouserPartNumber\": \"78L05\",    \"partSearchOptions\": \"None\"  }}"
```

# Scrapper

* https://github.com/kaddaGH/mouser-scraper
  ??? Ruby
