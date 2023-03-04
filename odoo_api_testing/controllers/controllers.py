import json
import time
from odoo import http
import math
import urllib3
import datetime

class OdooApiTesting(http.Controller): 
    
    ### Change Password
    @http.route('/api/changePassword',auth='none',type='http',csrf=False,methods=['POST'])
    def change_password(self,**kw):
        try:
            if (http.request.session.uid != None):
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    new_password = value['new_password']
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                for u in user:
                    u.write({
                        "password":new_password
                    })
                return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'result':{'status':'Successfully Changed Password'}}),headers = {"content-type":"application/json"})    
            else:
                return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':'Session expired'}),headers = {"content-type":"application/json"})    
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers = {"content-type":"application/json"})    
    
    ### Reset Password
    @http.route('/api/resetPassword', auth='none',type='http',csrf=False,methods=['POST'])
    def reset_password(self,**kw):
        try:
            new_password = None
            email = None
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                new_password = value['new_password']
                email = value['login']
            user = http.request.env['res.users'].sudo().search([('login','ilike',email)])
            for u in user:
                u.write({
                    "password":new_password
                })
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'result':{'status':'Successfully Changed Password'}}),headers = {"content-type":"application/json"})    
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers = {"content-type":"application/json"})    
  
    #### Register User
    @http.route('/api/register', auth='public',type='http',csrf=False,methods=['POST'])
    def register(self,**kw):
        try:
            user_password = None
            email = None
            name = None
            mobile = None
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                user_password = value['password']
                email = value['login']
                name = value['name']
                if (value.get('mobile')):
                    mobile = value['mobile']
            if http.request.env["res.users"].sudo().search([("login", "ilike", email)]):
                return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Failed, user already exist!"}),headers = {'content-type':'application/json'})
            if http.request.env["res.users"].sudo().search([("mobile", "ilike", mobile)]):
                    return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Failed, mobile number already exist!"}),headers = {'content-type':'application/json'})       
            user = http.request.env['res.users'].sudo().create({
                    'name':name,
                    'password':user_password,
                    'login':email,
                })
            user_id = user.partner_id.id
            user_details = http.request.env['res.partner'].sudo().search([('id','=',user_id)])
            for user in user_details:
                user.write({
                    "mobile":mobile,
                    "email":email
                })
            return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Registered User"}}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})

    ### login user
    @http.route('/api/login', type='http', auth="none",csrf=False,methods=["POST"])        
    def authenticate(self,**kw):
        try:
            password = None
            email = None
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                    password = value['password']
                    email = value['login']
            http.request.session.authenticate("odoo", email, password)
            user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
            cart = http.request.env['cart'].sudo().search([('partner_id.id','=',user.partner_id.id)])
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{
                "vip":user.partner_id.vip,
                "have_items_in_cart":True if cart else False,
                "partner_id":user.partner_id.id,
                "user_id":user.id,
                "name":user.partner_id.name,
                "email":user.partner_id.email,
                "mobile":user.partner_id.mobile if user.partner_id.mobile else "",
                "dob":str(user.partner_id.dob) if user.partner_id.dob else "",
                "image":('data:image/jpeg;base64,'+(user.partner_id.image_1920).decode("UTF-8")) if (user.partner_id.image_1920) else ""
            }}),headers = {'content-type':'application/json'})  
        except Exception as e:
            return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
             
    ### Logout
    @http.route('/api/logout', type='http', auth="none",csrf=False)
    def destroy(self):
        headers = {'Content-Type':'application/json'}
        try:
            if (http.request.session.uid != None):
                http.request.session.logout()
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Logged out'}}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Session expired'}}), headers=headers)
        except Exception as e:
             return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Update user info 
    @http.route('/api/updateUserInfo',auth="none" , type='http',csrf=False,methods=['PUT','POST'])
    def update_user_info(self,**kw):
        try:
            if(http.request.session.uid != None):
                image = None
                dob = None
                name = None
                json_object = json.loads(http.request.httprequest.data)
                user_data = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])       
                for key,value in json_object.items():
                    if (value.get('name')):
                        name = value['name']
                    else:
                        name = user_data.partner_id.name
                    if (value.get('image')):
                        image = value['image']
                    else:
                        image = user_data.partner_id.image_1920
                    if (value.get('dob')):
                        dob = value['dob']
                    else:
                        dob = user_data.partner_id.dob
                for record in user_data:
                    record.write({
                        "name":name,
                     })
                    partner = http.request.env['res.partner'].sudo().search([('id','=',record.partner_id.id)])
                    for p in partner:
                        p.write({
                            "dob":dob,
                            "image_1920":image
                        })
                return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Updated User Info"}}),headers = {'content-type':'application/json'})
            else:
                return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Update Email Address
    @http.route('/api/updateEmail',auth="none" , type='http',csrf=False,methods=['PUT','POST'])
    def update_email(self,**kw):
        try:
            if(http.request.session.uid != None):
                email = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    email = value['email']
                user_data = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                if http.request.env["res.users"].sudo().search([("login", "ilike", email)]):
                    return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Failed, user already exist!"}),headers = {'content-type':'application/json'})       
                for record in user_data:
                    record.write({
                        "login":email,
                     })
                    partner = http.request.env['res.partner'].sudo().search([('id','=',record.partner_id.id)])
                    for p in partner:
                        p.write({
                            "email":email,
                        })
                return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Updated Email Address"}}),headers = {'content-type':'application/json'})
            else:
                return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Update Phone Number
    @http.route('/api/updateMobile',auth="none" , type='http',csrf=False,methods=['PUT','POST'])
    def update_mobile_number(self,**kw):
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])        
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    mobile = value['mobile']
                if http.request.env["res.users"].sudo().search([("mobile", "=", mobile)]):
                    return http.Response (json.dumps({"jsonrpc":"2.0","id":None,"error":"Failed, mobile number already exist!"}),headers = {'content-type':'application/json'})       
                for record in user:
                    partner = http.request.env['res.partner'].sudo().search([('id','=',user.partner_id.id)])
                    for p in partner:
                        p.write({
                            "mobile":mobile,
                        })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Updated Mobile Number"}}),headers = {'content-type':'application/json'}) 
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers = {'content-type':'application/json'}) 
        except Exception as e:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 
    
    ### Product
    @http.route('/api/getAllProducts', auth='public',type="http",csrf=False,methods=['POST'])
    def get_products_filtered(self,**kw):
        try:
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                page_number = value['page']
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            total_products = http.request.env['product.product'].sudo().search([('detailed_type','=','product')])
            total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page) 
            products = http.request.env['product.template'].sudo().search([('detailed_type','=','product')],offset=offset,limit=per_page)
            product_details = []
            pagination = {}
            for product in products:
                    product_details.append({
                            'id':product.id,
                            'name':product.name,
                            'is_vip':product.vip,
                            'is_on_sale':product.sale,
                            'regular_price':product.list_price,
                            'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                            'category':product.categ_id.name,
                            'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                        })
            pagination = {
                "page":page_number if page_number > 0 else 1,
                "size":0 if product_details == [] else len(product_details),
                "total_pages":total_pages
            }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"products":product_details,"pagination":pagination}}),headers = {'content-type':'application/json'}) 
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 
    
    ### Get Product By id (single page)
    @http.route('/api/getProduct/<id>', auth='public',type='http',csrf=False,methods=['GET'])
    def get_products_by_id(self,id):
        headers = {'Content-Type': 'application/json'}
        try:
            products = http.request.env['product.product'].sudo().search([("id",'=',id)])
            product_details = {}
            status = None
            for product in products:
                wishlist = http.request.env['wishlist'].sudo().search([('product_id.id','=',product.id)])
                attributes = http.request.env['product.template.attribute.value'].sudo().search([('product_tmpl_id.id','=',product.id)])
                images = http.request.env['product.image'].sudo().search([('product_tmpl_id.id','=',product.id)])
                if product.qty_available <= 0:
                    status = False
                else:
                    status = True
                product_details={
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'is_in_wishlist':True if wishlist else False,
                    'is_vip_charge_product':True if product.name == "vip charge" else False,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'quantity':1,
                    'quantity_available':int(product.qty_available),
                    'in_stock':status,
                    'description':product.description_sale if product.description_sale else "",
                    "specifications":[{"name":att.attribute_id.name,"value":att.name} for att in attributes],
                    'images':list(map(lambda img:('data:image/png;base64,'+(img.image_1920).decode("UTF-8")), images))
                }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":product_details}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)
     
    ### Search Products
    @http.route('/api/search', auth='public',type='http',csrf=False,methods=['POST'])
    def search(self,**kw):
        try:
            product_name = ""
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                page_number = value['page']
                product_name = value['name']
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type",'=',"product")],limit=per_page,offset=offset)
            total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('detailed_type','=','product')])
            total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            product_details = []
            pagination ={}
            for product in products:
                product_details.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    "image":('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                    "page":page_number if page_number > 0 else 1,
                    "size":0 if product_details == [] else len(product_details),
                    "total_pages":total_pages
                }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"products":product_details,"pagination":pagination}}),headers = {'content-type':'application/json'}) 
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 
    
    ### Get all categories
    @http.route('/api/getCategories',auth='public',type='http',csrf=False,methods=['GET'])
    def get_Categories(self):
        headers = {'Content-Type':"application/json"}
        try:
            category = http.request.env['product.category'].sudo().search([("id","!=",1)],order='priority asc')
            categories = []
            for cat in category:
                if cat.parent_id.id == False:
                        categories.append({
                            "id":cat.id,
                            "name":cat.name,
                            "image":('data:image/png;base64,'+(cat.image).decode("UTF-8")) if cat.image != False else ""
                        })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":categories}), headers=headers)
        except Exception as e:
            headers = {'Content-Type':"application/json"}
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'error':str(e)}}), headers=headers)
    
    ### Get Subcategories by Category
    @http.route('/api/getSubcategoriesByCategory/<id>',auth='public',type='http',csrf=False,methods=['GET'])
    def get_products_by_category(self,id,**kw):
        try:
            sub_category = http.request.env['product.category'].sudo().search([("parent_id.id",'=',id)])
            categories = []
            for categ in sub_category:
                categories.append({
                    "id":categ.id,
                    "name":categ.name,
                })
            categories.append({
                "id":1,
                "name":"All"
            })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":categories}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Get Product by Subcategory 
    @http.route('/api/getProductsBySubcategory',auth='public',type='http',csrf=False,methods=['POST'])
    def get_products_by_subcategory(self,**kw):
        try:
            products_list = []
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            category_id = None
            sub_categ_id = None
            product_name = ""
            for key,value in json_object.items():
                if(value.get('name')):
                    product_name = value['name']
                category_id = value['category_id']
                page_number = value['page']
                if (value.get('subcategory_id')):
                    sub_categ_id = value['subcategory_id']
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            pagination = {}
            if (sub_categ_id != None):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("categ_id.id","=",sub_categ_id),('detailed_type', '=', 'product')],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("categ_id.id","=",sub_categ_id),('detailed_type', '=', 'product')])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            else:
                category = http.request.env['product.category'].sudo().search([("parent_id.id",'=',category_id)]).ids
                category_ids = []
                for i in category:
                    category_ids.append(i)
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("categ_id.id","in",category_ids),('detailed_type', '=', 'product')],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("categ_id.id","in",category_ids),('detailed_type','=','product')])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            for product in products:
                products_list.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                    "page":page_number if page_number > 0 else 1,
                    "size":0 if products_list == [] else len(products_list),
                    "total_pages":total_pages
                }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"products":products_list,"pagination":pagination}}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Get all brands 
    @http.route('/api/getBrands',auth='public',type='http',csrf=False,methods=['GET'])
    def get_brands(self):
        headers = {'Content-Type':"application/json"}
        try:
            brand = http.request.env['product.attribute'].sudo().search([('name','=',"Brand")])
            brands = []
            for brand in brand:
                brand_values = http.request.env['product.attribute.value'].sudo().search([('attribute_id.id','=',brand.id)])
                for b in brand_values:
                    brands.append({
                        "id":b.id,
                        "name":b.name,
                        "image":('data:image/png;base64,'+(b.image).decode("UTF-8")) if b.image != False else ""
                    })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":brands}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':str(e)}), headers=headers)

    ### Get brands by id
    @http.route('/api/getSubcategoriesByBrand/<id>',auth='public',type='http',csrf=False,methods=['GET'])
    def get_products_by_brand(self,id,**kw):
        try:
            categories = []
            brands = http.request.env['product.template.attribute.value'].sudo().search(['&',('product_attribute_value_id.id','=',id),('attribute_id.name','=',"Brand")])
            brandss = []
            for b in brands:
                brandss.append(b.product_tmpl_id.id)
            product_category = http.request.env['product.template'].sudo().search(['&',('id','in',brandss),("detailed_type","=","product")])
            category_ids = []
            for p in product_category:
                category_ids.append(p.categ_id.id)
            category = http.request.env['product.category'].sudo().search([("id",'in',category_ids)])
            for categ in category:
                categories.append({
                    'id':categ.id,
                    'name':categ.name
                })
            categories.append({
                "id":1,
                "name":"All"
            })
            unique = list({ each['id'] : each for each in categories }.values())
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":unique}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})
    
    ### Get Products by Category from Brand
    @http.route('/api/getProductsByBrandSubcategory',auth='public',type='http',csrf=False,methods=['POST'])
    def get_products_by_categ_in_brand(self,**kw):
        try:
            categ_id = None
            brand_id = None
            page_number = 0
            product_name = ""
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                    if(value.get('name')):
                        product_name = value['name']
                    brand_id = value['brand_id']
                    if (value.get('subcategory_id')):
                        categ_id = value['subcategory_id']
                    page_number = value['page']
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            products = []
            pagination={}
            brand_values = http.request.env['product.template.attribute.value'].sudo().search(['&',('product_attribute_value_id.id','=',brand_id),('attribute_id.name','=',"Brand")])
            brands = []
            for b in brand_values:
                brands.append(b.product_tmpl_id.id)
            if (categ_id != None):
                product = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('id','in',brands),('categ_id.id','=',categ_id),("detailed_type","=","product")],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('id','in',brands),('categ_id.id','=',categ_id),("detailed_type","=","product")])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            else:
                product = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('id','in',brands),("detailed_type","=","product")],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('id','in',brands),("detailed_type","=","product")])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            for product in product:
                products.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                    "page":page_number if page_number > 0 else 1,
                    "size":0 if products == [] else len(products),
                    "total_pages":total_pages
                }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"products":products,"pagination":pagination}}),headers = {'content-type':'application/json'})
        except Exception as e:
             return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'})

    ### Order Details
    @http.route('/api/getDeliveryOrders',auth='none',type='http',csrf=False,methods=['GET'],)
    def get_order_details(self):
        headers = {'Content-Type': 'application/json'}
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                partner = http.request.env['res.partner'].sudo().search([('parent_id.id','=',user.partner_id.id)]).ids
                orders = http.request.env['sale.order'].sudo().search(["|",("partner_id.id",'=',user.partner_id.id),('partner_id.id','in',partner)]) 
                order_list = []
                for order in orders:
                    stock = http.request.env['stock.picking'].sudo().search([('origin','ilike',order.name)])
                    order_list.append({
                        'id':order.id,
                        'order_nb':order.name,
                        'status':"Packaging" if stock.state == "assigned" else "On the way" if stock.state == "on_the_way" else "Delivered" if stock.state == "done" else "Cancelled" if stock.state == "cancel" else "Order Received",
                        "total":round(order.amount_total,3)
                        }) 
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":order_list}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':'Session expired'}), headers=headers)
        except Exception as e:
               return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':str(e)}), headers=headers)

    ### Order Details by Id
    @http.route('/api/getDeliveryOrder/<id>',auth='none',type='http',csrf=False,methods=['GET'],)
    def get_order_details_by_id(self,id):
        headers = {'Content-Type': 'application/json'}
        try:
            if (http.request.session.uid != None):
                orders = http.request.env['sale.order'].sudo().search([('id','=',id)]) 
                order_list = {}
                if orders:
                    for order in orders:
                        order_lines = http.request.env['sale.order.line'].sudo().search([('order_id.id','=',order.id)])
                        stock = http.request.env['stock.picking'].sudo().search([('origin','ilike',order.name)])
                        order_list = {
                            'id':order.id,
                            'order_nb':order.name,
                            'status':"Packaging" if stock.state == "assigned" else "On the way" if stock.state == "on_the_way" else "Delivered" if stock.state == "done" else "Cancelled" if stock.state == "cancel" else "Order Received",
                            'payment_method':order.payment_method,
                            'address':{
                                'name':order.partner_id.name,
                                'email':order.partner_id.email if (order.partner_id.email != False)  else "",
                                'street':order.partner_id.street if (order.partner_id.street != False)  else "",
                                'street2':order.partner_id.street2 if (order.partner_id.street != False)  else "",
                                'zip':order.partner_id.zip if (order.partner_id.zip != False)  else "",
                                'city':order.partner_id.city if (order.partner_id.city != False)  else "",
                                'mobile':order.partner_id.mobile if (order.partner_id.mobile != False)  else ""
                            },
                            'order_lines':[(dict(id=ol.product_id.product_tmpl_id.id,name=ol.name,quantity=int(ol.product_uom_qty),subtotal=ol.price_subtotal)) for ol in order_lines],
                            "total_without_vat":round(order.amount_untaxed,2),
                            "VAT_percentage":"11%",
                            "VAT_amount":order.amount_tax,
                            "total":round(order.amount_total,2)
                            }   
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":order_list}), headers=headers)
                else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"No Order Found"}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers=headers)
        except Exception as e:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### Add to cart 
    @http.route('/api/addToCart', auth='none',type='http',csrf=False,website=False,methods=['POST'])
    def add_to_cart(self,**kw):
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])
                product_id = None
                quantity = None
                is_vip_price = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    product_id = value['product_id']
                    quantity = value['quantity']
                    if (value.get('is_vip_price')):
                        is_vip_price = value['is_vip_price']
                product = http.request.env['cart'].sudo().search(['&',('partner_id.id','=',user.partner_id.id),('product_id.id','=',product_id)])
                if user.partner_id.is_vip == True:
                        if product:
                                product.write({
                                    "quantity":product.quantity + quantity
                                })
                        else:
                            http.request.env['cart'].with_user(user.id).create({
                                    'partner_id': user.partner_id.id,
                                    'product_id': product_id,
                                    "quantity":quantity,
                        })
                else:      
                    if is_vip_price != True or is_vip_price == "":
                        if product:
                            product.write({
                                "quantity":product.quantity + quantity
                            })
                        else:
                            http.request.env['cart'].with_user(user.id).create({
                                    'partner_id': user.partner_id.id,
                                    'product_id': product_id,
                                    "quantity":quantity,
                                })
                    else:
                        product_with_vip = http.request.env['cart'].sudo().search(['&',('partner_id.id','=',user.partner_id.id),("product_id.name",'ilike',"vip charge")])
                        vip_charge = http.request.env['product.template'].sudo().search([('name','ilike','vip charge')])
                        if product_with_vip:
                            if product:
                                    product.write({
                                        "quantity":product.quantity + quantity
                                    })
                            else:
                                    http.request.env['cart'].with_user(user.id).create({
                                            'partner_id': user.partner_id.id,
                                            'product_id': product_id,
                                            "quantity":quantity,
                                    })
                        else:
                            partner = http.request.env['res.partner'].sudo().search([('parent_id.id','=',user.partner_id.id)]).ids
                            orders = http.request.env['stock.picking'].sudo().search(["&",('state','!=','cancel'),"|",("partner_id.id",'=',user.partner_id.id),('partner_id.id','in',partner)]) 
                            canceled_orders = http.request.env['stock.picking'].sudo().search(["&",('state','ilike','cancel'),"|",("partner_id.id",'=',user.partner_id.id),('partner_id.id','in',partner)]) 
                            can_add_vip = False
                            products = []
                            products_in_cancel = []
                            print (canceled_orders)
                            print(orders)
                            if canceled_orders and not orders:
                                for co in canceled_orders:
                                    order_liness = http.request.env['sale.order.line'].sudo().search([('order_id.name','=',co.origin)])
                                    for oll in order_liness:
                                        products_in_cancel.append(oll.name)
                                        if "vip charge" in products_in_cancel:
                                            can_add_vip = True
                            elif not canceled_orders and orders:
                                for o in orders:
                                    order_line = http.request.env['sale.order.line'].sudo().search([('order_id.name','=',o.origin)])
                                    for ol in order_line:
                                        products.append(ol.name)
                                        if "vip charge" in products:
                                            can_add_vip = False
                                        else:
                                            can_add_vip = True
                            elif canceled_orders and orders:
                                for o in orders:
                                    order_line = http.request.env['sale.order.line'].sudo().search([('order_id.name','=',o.origin)])
                                    for ol in order_line:
                                        products.append(ol.name)
                                        if "vip charge" in products:
                                            can_add_vip = False
                                        else:
                                            can_add_vip = True
                            else:
                                    can_add_vip = True
                            print(products_in_cancel)
                            print (products)    
                            print (can_add_vip)
                            if (can_add_vip == True):
                                http.request.env['cart'].with_user(user.id).create({
                                        'partner_id': user.partner_id.id,
                                        'product_id': vip_charge.id,
                                        "quantity":1,
                                    })
                                if product:
                                    product.write({
                                        "quantity":product.quantity + quantity
                                    })
                                else:
                                    http.request.env['cart'].with_user(user.id).create({
                                            'partner_id': user.partner_id.id,
                                            'product_id': product_id,
                                            "quantity":quantity,
                                    })
                            else:
                                    if product:
                                        product.write({
                                            "quantity":product.quantity + quantity
                                        })
                                    else:
                                        http.request.env['cart'].with_user(user.id).create({
                                                'partner_id': user.partner_id.id,
                                                'product_id': product_id,
                                                "quantity":quantity,
                                    })            
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Added to Cart"}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
                 return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})

    ### View Cart
    @http.route('/api/viewCart',auth="none",type="http",csrf=False,methods=["GET"])
    def view_cart(self):
        headers = {"content-type":"application/json"}
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                cart_list = http.request.env['cart'].sudo().search([('partner_id.id',"=",user.partner_id.id)])
                cart_data = []
                status = None
                for cart in cart_list:
                    product = http.request.env['product.template'].sudo().search([("id",'=',cart.product_id.id)])
                    for p in product:
                        if p.qty_available <=0:
                            status = False
                        else:
                            status = True
                        cart_data.append({
                                "id":p.id,
                                "name":p.name,
                                'is_vip':p.vip,
                                'is_on_sale':p.sale,
                                'is_vip_charge_product':True if p.name == "vip charge" else False,
                                "regular_price":p.list_price,
                                "new_price":p.vip_price if p.vip == True else p.sale_price if p.sale == True else 0.0,
                                "quantity":int(cart.quantity),
                                "quantity_available":int(p.qty_available),
                                "in_stock":status,
                                "image":('data:image/png;base64,'+(p.image_1920).decode("utf-8"))  if p.image_1920 != False else ""
                            })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":cart_data}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'error':'Session expired'}}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'error':str(e)}}), headers=headers)
    
    ### Update Cart Quantity
    @http.route('/api/updateCartQuantity',auth="none",type="http",csrf=False,methods=["PUT","POST"])
    def update_cart_quantity(self,**kw):
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                json_object = json.loads(http.request.httprequest.data)
                quantity = None
                product_id = None
                for key,value in json_object.items():
                    product_id = value['product_id']
                    quantity = value['quantity']
                cart_list = http.request.env['cart'].sudo().search(['&',('partner_id.id',"=",user.partner_id.id),('product_id.id','=',product_id)])
                for record in cart_list:
                    record.write({
                        "quantity":quantity,
                    })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Updated Quantity in Cart"}}),headers = {'content-type':'application/json'}) 
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers = {'content-type':'application/json'}) 
        except Exception as e:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 
    
    ### Remove Product From Cart
    @http.route('/api/removeFromCart', auth='none',type='http',csrf=False,website=False,methods=['POST','DELETE'])
    def remove_from_cart(self,**kw):
        try:
            if (http.request.session.uid != None):
                product_id = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    product_id = value['product_id']
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                http.request.env['cart'].sudo().search(['&',('partner_id.id',"=",user.partner_id.id),('product_id.id','=',product_id)]).unlink()
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Successfully Removed from Cart'}}), headers={'content-type':'application/json'})
            else:
                 return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':'Session expired'}), headers={'content-type':'application/json'})
        except Exception as e:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':'Session expired'}), headers={'content-type':'application/json'})

    ### Create Delivery Order
    @http.route('/api/deliveryOrder',auth="none",type="http",csrf=False,methods=["POST"])
    def create_delivery_order(self,**kw):
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])
                partner_shipping_id = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    partner_shipping_id = value['address_id']
                order = http.request.env['sale.order'].with_user(user.id).create({
                    'partner_id': partner_shipping_id,
                    'partner_invoice_id':partner_shipping_id,
                    'partner_shipping_id':partner_shipping_id,
                    'date_order':datetime.datetime.now(),
                    "website_id":1,
                    "company_id":user.company_id.id,
                })
                order_id = order.id
                order_lines = []
                data = json.loads(http.request.httprequest.data)
                json_data = json.dumps(data)
                resp = json.loads(json_data)
                for i in resp['params']['order_lines']:
                    product_id = http.request.env['product.product'].sudo().search([('product_tmpl_id.id','=',i['product_id'])])
                    if i['is_vip_price'] == True:
                        order_lines.append({
                            "order_id":order_id,
                            "product_id":product_id.id,
                            "name":product_id.product_tmpl_id.name,
                            "price_unit":product_id.product_tmpl_id.vip_price if product_id.product_tmpl_id.vip == True else product_id.product_tmpl_id.sale_price if product_id.product_tmpl_id.sale == True else product_id.product_tmpl_id.list_price,
                            "product_uom_qty":i['quantity'],
                            "company_id":user.company_id.id,
                            "currency_id":user.company_id.currency_id.id
                        })
                    else:
                        order_lines.append({
                        "order_id":order_id,
                        "product_id":product_id.id,
                        "name":product_id.product_tmpl_id.name,
                        "price_unit":product_id.product_tmpl_id.list_price if product_id.product_tmpl_id.vip == True else product_id.product_tmpl_id.sale_price if product_id.product_tmpl_id.sale == True else product_id.product_tmpl_id.list_price,
                        "product_uom_qty":i['quantity'],
                        "company_id":user.company_id.id,
                        "currency_id":user.company_id.currency_id.id
                    })
                order_line = http.request.env['sale.order.line'].with_user(user.id).create(order_lines)
                empty_cart = http.request.env['cart'].sudo().search([('partner_id.id',"=",user.partner_id.id)]).unlink()
                http_request = None
                http_request = urllib3.PoolManager()
                encoded_body = json.dumps({"read":False,"order_nb":order.name,"time":int(round(datetime.datetime.now().timestamp())),"status":"Order Received"})
                http_request.request("PUT", "https://quico-tech-default-rtdb.europe-west1.firebasedatabase.app/Orders/"+str(user.id)+"/"+str(order_id)+".json",body=encoded_body,headers={"content-type":"application/json","auth":"AIzaSyDaoLknXHqhJY_zcKlAxV2UX0tnl0OdM5w"})
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Created Delivery Order"}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})

    ### Get Delivery Addresses
    @http.route('/api/getDeliveryAddresses',auth="none" , type='http',csrf=False,methods=['GET'])
    def get_addresses(self):
        headers = {'Content-Type': 'application/json'}
        try:
            if (http.request.session.uid != None):
                address = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                other = []
                for add in address:
                    child_address = http.request.env['res.partner'].sudo().search([('parent_id.id',"=",add.partner_id.id)])
                    for child in child_address:
                        other.append({
                            "id":child.id,
                            "name":child.name if (child.name != False) else "",
                            "street":child.street if (child.street != False) else "",
                            "street2":child.street2 if (child.street2 != False) else "",
                            "country":child.country_id.name if (child.country_id.name != False) else "",
                            "city":child.city if (child.city != False) else "",
                            "zip":child.zip if (child.zip != False) else "",
                            "mobile":child.mobile if (child.mobile != False) else "",
                        })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":other}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':"Session expired"}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,'error':str(e)}), headers=headers)

    ### Get Delivery Addresses By Id
    @http.route('/api/getDeliveryAddresses/<id>',auth="none" , type='http',csrf=False,methods=['GET'])
    def get_addresses_by_id(self,id):
        headers = {'Content-Type': 'application/json'}
        try:
            if (http.request.session.uid != None):
                address = http.request.env['res.partner'].sudo().search([('id','=',id)])
                main={}
                for add in address:
                    main = {
                            "id":add.id,
                            "name":add.name if (add.name != False) else "",
                            "street":add.street if (add.street != False) else "",
                            "street2":add.street2 if (add.street2 != False) else "",
                            "country":add.country_id.name if (add.country_id.name != False) else "",
                            "city":add.city if (add.city != False) else "",
                            "zip":add.zip if (add.zip != False) else "",
                            "mobile":add.mobile if (add.mobile != False) else "",
                        }
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":main}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### Update Delivery Address
    @http.route('/api/updateDeliveryAddress/<id>',auth="none" , type='http',csrf=False,methods=['PUT','POST'])
    def update_address(self,id,**kw):
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.partner'].sudo().search([('id',"=",id)])
                name = None
                street = None
                street2 = None
                city = None
                zip = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    if (value.get('name')):
                        name = value['name']
                    else:
                        name = user.name
                    if (value.get('street')):
                        street = value['street']
                    else:
                        street = user.street
                    if (value.get('street2')):
                        street2 = value['street2']
                    else:
                        street2 = user.street2
                    if (value.get('city')):
                        city = value['city']
                    else:
                        city = user.city
                    if (value.get('zip')):
                        zip = value['zip']
                    else:
                        zip = user.zip
                order = http.request.env['sale.order'].sudo().search([('partner_id.id','=',id)]).ids
                orders = []
                for i in order:
                    orders.append(i)
                if orders != []:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Cannot Update Delivery Address Since its Related to an Order"}), headers={'content-type':'application/json'})
                else:
                    for record in user:
                        record.write({
                            "name":name,
                            "street":street,
                            "street2":street2,
                            "city":city,
                            "zip":zip,
                        })
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Successfully Updated Delivery Address'}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})

    ### Create Delivery Address
    @http.route('/api/createDeliveryAddress', auth='none',type='http',csrf=False,website=False,methods=['POST'])
    def create_delivery_address(self,**kw):
        try:
            if (http.request.session.uid != None):
                name = None
                street = None
                street2 = None
                city = None
                zip = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    if (value.get('name')):
                        name = value['name']
                    if (value.get('street')):
                        street = value['street']
                    if (value.get('street2')):
                        street2 = value['street2']
                    if (value.get('city')):
                        city = value['city']
                    if (value.get('zip')):
                        zip = value['zip']
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])
                http.request.env['res.partner'].with_user(user.id).create({
                        'parent_id': user.partner_id.id,
                        'type': "delivery",
                        "name":name,
                        "street":street,
                        "street2":street2,
                        "country_id":126,
                        "city":city,
                        "zip":zip,
                        "mobile":user.partner_id.mobile,
                        "email":user.partner_id.email
                    })
                partner = http.request.env['res.partner'].sudo().search([('id',"=",user.partner_id.id)])
                for p in partner:
                    p.write({
                        "street":street,
                        "street2":street2,
                        "country_id":126,
                        "city":city,
                        "zip":zip,
                        "phone":user.partner_id.mobile
                    })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Successfully Created Delivery Address'}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})
    
    ### Remove Delivery Address
    @http.route('/api/removeDeliveryAddress', auth='none',type='http',csrf=False,website=False,methods=['POST','DELETE'])
    def remove_delivery_address(self,**kw):
        try:
            if(http.request.session.uid != None):
                id = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    id = value['id']
                order = http.request.env['sale.order'].sudo().search([('partner_id.id','=',id)]).ids
                orders = []
                for i in order:
                    orders.append(i)
                if orders != []:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Cannot Delete Delivery Address Since its Related to an Order"}), headers={'content-type':'application/json'})
                else:
                    http.request.env['res.partner'].sudo().search([('id',"=",id)]).unlink()
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':'Successfully Removed Delivery Address'}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})
    
    ### Get service types
    @http.route('/api/getServiceTypes/<id>',auth="public" , type='http',csrf=False,methods=['GET'])
    def get_service_types_by_id(self,id):
        headers = {'Content-Type': 'application/json'}
        try:
            service_type = http.request.env['fsm.order.type'].sudo().search(['&',('parent_id','=',False),("service_id.id","=",id)])
            service_types = []
            for serv in service_type:
                service_types.append({
                    "id":serv.id,
                    "type":serv.name,
                    "image":('data:image/png;base64,'+(serv.image).decode("UTF-8")) if serv.image != False else "",
                    "have_sub_service":serv.have_sub
                })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":service_types}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### Get service types
    @http.route('/api/getSubServiceType/<id>',auth="public" , type='http',csrf=False,methods=['GET'])
    def get_sub_service_types_by_id(self,id,**kw):
        headers = {'Content-Type':'application/json'}
        try:
            sub_service_type = http.request.env['fsm.order.type'].sudo().search([("parent_id.id","=",id)],order='priority asc')
            sub_service_types = []
            for serv in sub_service_type:
                sub_service_types.append({
                    "id":serv.id,
                    "type":serv.name,
                    "priority":serv.priority,
                    "have_sub_service":serv.have_sub,
                    "image":('data:image/png;base64,'+(serv.image).decode("UTF-8")) if serv.image != False else "",
                })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":sub_service_types}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### get services 
    @http.route('/api/getServices',auth="public" , type='http',csrf=False,methods=['GET'])
    def get_service(self):
        headers = {'Content-Type': 'application/json'}       
        try:
            service = http.request.env['fsm.tag'].sudo().search([])
            services = []
            for serv in service:
                services.append({
                    "id":serv.id,
                    "name":serv.name,
                    "description":serv.description if serv.description != False else "",
                    "image":('data:image/png;base64,'+(serv.icon).decode("UTF-8")) if serv.icon != False else ""
                })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":services}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### Repair Form
    @http.route('/api/createServiceOrder', auth='none',type='http',csrf=False,website=False,methods=['POST'])
    def service_order(self,**kw):
        try:
            if(http.request.session.uid != None):
                service = None
                service_type = None
                delivery_type = None
                description = None
                image_1 = None
                image_2 = None
                image_3 = None
                image_4 = None
                audio = None
                audio_filename = None
                address = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    if (value.get('address_id')):
                        address = value['address_id']
                    if (value.get('service_id')):
                        service = value['service_id']
                    if (value.get('service_type_id')):
                        service_type = value['service_type_id']
                    if (value.get('delivery_type')):
                        delivery_type = value['delivery_type']
                    if (value.get('description')):
                        description = value['description']
                    if (value.get('audio')):
                        audio = value.get('audio')
                    if (value.get('audio_filename')):
                        audio_filename = value.get('audio_filename')
                    if (value.get('images')):
                        if (len(value.get('images')) == 4):
                            image_1 = value.get("images")[0]
                            image_2 = value.get("images")[1]
                            image_3 = value.get("images")[2]
                            image_4 = value.get("images")[3]
                        elif (len(value.get("images")) == 3):
                            image_1 = value.get("images")[0]
                            image_2 = value.get("images")[1]
                            image_3 = value.get("images")[2]
                        elif (len(value.get("images")) == 2): 
                            image_1 = value.get("images")[0]
                            image_2 = value.get("images")[1]
                        elif (len(value.get("images")) == 1):
                            image_1 = value.get("images")[0]
                        else:
                            pass    
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])
                service_order = http.request.env['fsm.order'].sudo().create({
                        'company_id':1,
                        'stage_id':1,
                        'team_id':1,
                        'partner_id': address if address else user.partner_id.id,
                        'service':[(4,service)],
                        'service_type': service_type,
                        'delivery_type':delivery_type,
                        'description':description,
                        'image_1':image_1,
                        'image_2':image_2,
                        'image_3':image_3,
                        'image_4':image_4,
                        'audio':audio,
                        'audio_file_name':audio_filename
                })
                http_request = None
                http_request = urllib3.PoolManager()
                encoded_body = json.dumps({"read":False,"time":int(round(datetime.datetime.now().timestamp())),"service_nb":service_order.name,"status":"Request Received"})
                http_request.request("PUT", "https://quico-tech-default-rtdb.europe-west1.firebasedatabase.app/Services/"+str(user.id)+"/"+str(service_order.id)+".json",body=encoded_body,headers={"content-type":"application/json","auth":"AIzaSyDaoLknXHqhJY_zcKlAxV2UX0tnl0OdM5w"})
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{'status':"Succefully Submitted Order"}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})

    ### Get Service Orders
    @http.route('/api/getServiceOrders', auth='none',type='http',csrf=False,website=False,methods=['GET'])
    def get_service_order(self):
        headers = {"content-type":"application/json"}
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                partner = http.request.env['res.partner'].sudo().search([('parent_id.id','=',user.partner_id.id)]).ids
                service = http.request.env['fsm.order'].sudo().search(["|",("partner_id.id",'=',user.partner_id.id),("partner_id.id",'in',partner)])
                service_orders = []
                for order in service:
                    service_orders.append({
                            'id':order.id,
                            'service_nb':order.name,
                            'status':"Request Received" if order.stage_id.id == 1 else "Waiting Response" if order.stage_id.id == 4 else "In Progress" if order.stage_id.id == 5 else "Completed" if order.stage_id.id == 2 else "Cancelled" if order.stage_id.id == 3 else "",
                        })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":service_orders}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)

    ### Get Service Orders
    @http.route('/api/getServiceOrder/<id>', auth='none',type='http',csrf=False,website=False,methods=['GET'])
    def get_service_order_by_id(self,id):
        headers = {"content-type":"application/json"}
        try:
            if(http.request.session.uid != None):
                service = http.request.env['fsm.order'].sudo().search([('id',"=",id)])
                service_order = {}
                images = []
                if service:
                    for order in service:
                        if (order.image_1):
                            images.append('data:image/jpeg;base64,'+(order.image_1).decode("UTF-8"))
                        if (order.image_2):
                            images.append('data:image/jpeg;base64,'+(order.image_2).decode("UTF-8"))
                        if (order.image_3):
                            images.append('data:image/jpeg;base64,'+(order.image_3).decode("UTF-8"))
                        if (order.image_4):
                            images.append('data:image/jpeg;base64,'+(order.image_4).decode("UTF-8"))
                        service_order = {
                                'id':order.id,
                                'service_nb':order.name,
                                'service': order.service.name,
                                'service_type':order.service_type.name,
                                'status':"Request Received" if order.stage_id.id == 1 else "Waiting Response" if order.stage_id.id == 4 else "In Progress" if order.stage_id.id == 5 else "Completed" if order.stage_id.id == 2 else "Cancelled" if order.stage_id.id == 3 else "",
                                'delivery_type':order.delivery_type,
                                "address":{
                                    "name":order.partner_id.name,
                                    "street":order.partner_id.street,
                                    "street2":order.partner_id.street2,
                                    "city":order.partner_id.city,
                                    "zip":order.partner_id.zip,
                                    "email":order.partner_id.email,
                                    "mobile":order.partner_id.mobile
                                } if order.delivery_type == "dtd" else {},
                                'problem_description':order.description if order.description != False else "",
                                'images':images,
                                'solution':order.resolution if order.resolution != False else "",
                                'scheduled_date_start':str(order.scheduled_date_start) if order.scheduled_date_start != False else "",
                                'scheduled_duration':order.scheduled_duration if order.scheduled_duration != False else "",
                                'scheduled_date_end':str(order.scheduled_date_end) if order.scheduled_date_end != False else ""
                            }
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":service_order}), headers=headers)
                else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"No Service Order Found"}), headers=headers)
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers=headers)
    
    ### Apply Survey
    @http.route('/api/applySurvey', auth='user',type='http',csrf=False,website=False,methods=['POST','PUT'])
    def apply_survey(self):
        try:
            headers = {"content-type":"application/json"}
            if(http.request.session.uid != None):
                json_object = json.loads(http.request.httprequest.data)
                id = None
                review = None
                rating = None
                for key,value in json_object.items():
                    id = value.get('order_id')
                    if value.get('review'):
                        review = value.get('review')
                    if value.get('rating'):
                        rating = value.get('rating')
                order = http.request.env['sale.order'].sudo().search([('id','=',id)])
                for o in order:
                    o.write({
                        'review':review,
                        'order_rate':int(rating)
                    })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Succefully Submitted!"}}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            headers = {"content-type":"application/json"}
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)     
    
    ### Notification Details
    @http.route('/api/notificationDetails', auth='user',type='http',csrf=False,website=False,methods=['POST','PUT'])
    def notification_details(self):
        try:
            headers = {"content-type":"application/json"}
            if(http.request.session.uid != None):
                json_object = json.loads(http.request.httprequest.data)
                id = None
                for key,value in json_object.items():
                    id = value.get('service_id')
                encoded_body = None
                service = http.request.env['fsm.order'].sudo().search([('id','=',id)])
                products = http.request.env['fsm.order.products'].sudo().search([('fsm_order_id.id','=',id)])
                situations = http.request.env['fsm.order.situation'].sudo().search([('fsm_order_id','=',id)])
                for s in service:
                    encoded_body = {
                            "service_nb":s.name,
                            "situation":[(dict(name=st.fsm_situation_id.name,exist=st.exist)) for st in situations], 
                            'products':[(dict(id=ol.product_id.id,name=ol.product_id.product_tmpl_id.name,quantity=int(ol.quantity),subtotal=ol.subtotal)) for ol in products],
                            'solution': s.resolution if s.resolution != False else "",
                            'scheduled_date_start':str(s.scheduled_date_start.strftime("%d-%m-%Y %H:%M:%S")) if s.scheduled_date_start != False else "",
                            'scheduled_date_end':str(s.scheduled_date_end.strftime("%d-%m-%Y %H:%M:%S")) if s.scheduled_date_end != False else "",
                            'duration':str(int(s.scheduled_duration))+" hours",
                        }
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":encoded_body}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            headers = {"content-type":"application/json"}
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)     

    ### Accept Request
    @http.route('/api/acceptRequest', auth='user',type='http',csrf=False,website=False,methods=['POST','PUT'])
    def accept_request(self):
        try:
            if(http.request.session.uid != None):
                headers = {"content-type":"application/json"}
                http_request = None
                http_request = urllib3.PoolManager()
                json_object = json.loads(http.request.httprequest.data)
                id = None
                for key,value in json_object.items():
                    id = value.get('service_id')
                partner = http.request.env['res.partner'].sudo().search([('parent_id.id','!=',False)])
                products = []
                data = json.loads(http.request.httprequest.data)
                json_data = json.dumps(data)
                resp = json.loads(json_data)
                dtaa = []
                for i in resp['params']:
                        dtaa.append(i)
                if 'products' in dtaa:
                    for i in resp['params']['products']:
                        products.append(i['product_id'])
                partners = []
                user = None
                for i in partner:
                    partners.append(i.id)
                serv_order = http.request.env['fsm.order'].sudo().search([('id','=',id)])
                for serv in serv_order:
                    if serv.partner_id.id in partners:
                        current_id = serv.partner_id.parent_id.id
                        user = http.request.env['res.users'].sudo().search([('partner_id.id','=',current_id)])
                    else:
                        user = http.request.env['res.users'].sudo().search([('partner_id.id','=',serv.partner_id.id)])
                    encoded_body = json.dumps({"read":False,"time":int(round(datetime.datetime.now().timestamp())),"service_nb":serv.name,"status":"In Progress"})
                    # http_request.request("PUT", "https://quico-tech-default-rtdb.europe-west1.firebasedatabase.app/Services/"+str(user.id)+"/"+str(serv.id)+".json",body=encoded_body,headers={"content-type":"application/json","auth":"AIzaSyDaoLknXHqhJY_zcKlAxV2UX0tnl0OdM5w"})
                    serv.write({
                        'stage_id':5
                    }) 
                service_products = http.request.env['fsm.order.products'].sudo().search([('fsm_order_id.id','=',id)])
                for p in service_products:
                    if p.product_id.id in products:
                        p.write({
                            'chosen_product':True
                        })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Accepted!"}}),headers=headers)     
            else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            headers = {"content-type":"application/json"}
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)     
        
    ### Reject Request
    @http.route('/api/rejectRequest', auth='user',type='http',csrf=False,website=False,methods=['POST','PUT'])
    def reject_request(self):
        try:
            if(http.request.session.uid != None):
                headers = {"content-type":"application/json"}
                http_request = None
                http_request = urllib3.PoolManager()
                json_object = json.loads(http.request.httprequest.data)
                id = None
                for key,value in json_object.items():
                    id = value.get('service_id')
                partner = http.request.env['res.partner'].sudo().search([('parent_id.id','!=',False)])
                partners = []
                user = None
                for i in partner:
                    partners.append(i.id)
                serv_order = http.request.env['fsm.order'].sudo().search([('id','=',id)])
                for serv in serv_order:
                    if serv.partner_id.id in partners:
                        current_id = serv.partner_id.parent_id.id
                        user = http.request.env['res.users'].sudo().search([('partner_id.id','=',current_id)])
                    else:
                        user = http.request.env['res.users'].sudo().search([('partner_id.id','=',serv.partner_id.id)])
                    encoded_body = json.dumps({"read":False,"time":int(round(datetime.datetime.now().timestamp())),"service_nb":serv.name,"status":"Cancelled"})
                    http_request.request("PUT", "https://quico-tech-default-rtdb.europe-west1.firebasedatabase.app/Services/"+str(user.id)+"/"+str(serv.id)+".json",body=encoded_body,headers={"content-type":"application/json","auth":"AIzaSyDaoLknXHqhJY_zcKlAxV2UX0tnl0OdM5w"})
                    serv.write({
                        'stage_id':3
                    }) 
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Rejected!"}}),headers=headers)     
            else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            headers = {"content-type":"application/json"}
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)     
    
    ### Add to wishlist
    @http.route('/api/addToWishlist', auth='none',type='http',csrf=False,website=False,methods=['POST'])
    def add_to_wishlist(self,**kw):
        headers = {'content-Type':'application/json'}
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                product_id = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    product_id = value['product_id']
                product = http.request.env['wishlist'].sudo().search(['&',('partner_id.id','=',user.partner_id.id),('product_id.id','=',product_id)])
                if product:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Product Already in Wishlist"}),headers=headers)     
                else:
                    http.request.env['wishlist'].with_user(user.id).create({
                        'partner_id':user.partner_id.id,
                        'product_id':product_id
                    }) 
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Added to Wishlist!"}}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)     

    ### View Wishlist
    @http.route('/api/viewWishlist', auth='none',type='http',csrf=False,website=False,methods=['GET'])
    def view_wishlist(self):
        headers = {'content-type':'application/json'}
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                wishlist = http.request.env['wishlist'].sudo().search([('partner_id.id','=',user.partner_id.id)])
                products = []
                for w in wishlist:
                    product = http.request.env['product.template'].sudo().search([("id",'=',w.product_id.id)])
                    for p in product:
                        products.append({
                            "id":p.id,
                            "name":p.name,
                            'is_vip':p.vip,
                            'is_on_sale':p.sale,
                            'regular_price':p.list_price,
                            'new_price':p.vip_price if p.vip == True else p.sale_price if p.sale == True else 0.0,
                            'category':p.categ_id.name,
                            'image':('data:image/png;base64,'+(p.image_1920).decode("UTF-8")) if p.image_1920 != False else ""
                        })
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":products}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers) 
            
    ### Add to wishlist
    @http.route('/api/removeFromWishlist', auth='none',type='http',csrf=False,website=False,methods=['POST','DELETE'])
    def delete_from_wishlist(self,**kw):
        headers = {'Content-Type':'application/json'}
        try:
            if(http.request.session.uid != None):
                product_id = None
                json_object = json.loads(http.request.httprequest.data)
                for key,value in json_object.items():
                    product_id = value['product_id']
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                http.request.env['wishlist'].sudo().search(['&',('partner_id.id',"=",user.partner_id.id),('product_id.id','=',product_id)]).unlink()
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Removed from Wishllist"}}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)   
        
    #### Home Page
    @http.route('/api/homepage',auth="public",type="http",csrf=False,methods=["GET"])
    def home_page(self):
        headers = {'Content-Type':"application/json"}
        try:
            service = http.request.env['fsm.tag'].sudo().search([])
            services= []
            for serv in service:
                services.append({
                    "id":serv.id,
                    "name":serv.name,
                    "image":('data:image/png;base64,'+(serv.icon).decode("UTF-8")) if serv.icon != False else ""
                })
            category = http.request.env['product.category'].sudo().search([("id","!=",1)])
            categories = []
            for cat in category:
                if cat.parent_id.id == False:
                        categories.append({
                            "id":cat.id,
                            "name":cat.name,
                            "image":('data:image/png;base64,'+(cat.image).decode("UTF-8")) if cat.image != False else ""
                        })
            vip = http.request.env['product.template'].sudo().search(['&',("vip","=",True),('detailed_type', '=', 'product')],limit=10)
            vip_products = []
            for v in vip:
                vip_products.append({
                    "id":v.id,
                    "name":v.name,
                    'category':v.categ_id.name,
                    'is_vip':v.vip,
                    'regular_price':v.list_price,
                    'new_price':v.vip_price if v.vip == True else v.sale_price if v.sale == True else 0.0,
                    "image":('data:image/png;base64,'+(v.image_1920).decode("UTF-8")) if (v.image_1920) else ""
                }) 
            brand = http.request.env['product.attribute'].sudo().search([('name','=',"Brand")])
            brands = []
            for brand in brand:
                brand_values = http.request.env['product.attribute.value'].sudo().search([('attribute_id.id','=',brand.id)])
                for b in brand_values:
                    brands.append({
                        "id":b.id,
                        "name":b.name,
                        "image":('data:image/png;base64,'+(b.image).decode("UTF-8")) if (b.image != False)  else ""
                    })
            bundles = []
            challenges = []
            hot_deal = http.request.env['product.template'].sudo().search(['&',("hot_deal","=",True),("detailed_type","=","product")],limit=10)
            hot_deals = []
            for h in hot_deal:
                hot_deals.append({
                    "id":h.id,
                    "name":h.name,
                    'category':h.categ_id.name,
                    'is_on_sale':h.sale,
                    'regular_price':h.list_price,
                    'new_price':h.vip_price if h.vip == True else h.sale_price if h.sale == True else 0.0,
                    "image":('data:image/png;base64,'+(h.image_1920).decode("UTF-8")) if (h.image_1920) else ""
                })
            best_sell = http.request.env['sale.order.line'].sudo().search([('product_id.product_tmpl_id.detailed_type','ilike','product')]) 
            best_sellers = []
            for product in best_sell:
                best_sellers.append({
                    'id':product.product_id.product_tmpl_id.id,
                    'name':product.product_id.product_tmpl_id.name,
                    'is_vip':product.product_id.product_tmpl_id.vip,
                    'is_on_sale':product.product_id.product_tmpl_id.sale,
                    'regular_price':product.product_id.product_tmpl_id.list_price,
                    'new_price':product.product_id.product_tmpl_id.vip_price if product.product_id.product_tmpl_id.vip == True else product.product_id.product_tmpl_id.sale_price if product.product_id.product_tmpl_id.sale == True else 0.0,
                    'category':product.product_id.product_tmpl_id.categ_id.name,
                    'image':('data:image/png;base64,'+(product.product_id.product_tmpl_id.image_1920).decode("UTF-8")) if product.product_id.product_tmpl_id.image_1920 != False else ""
                })
            ids = []
            sorted_ids = []
            for i in best_sellers:
                ids.append(i['id'])
            my_dict = {item: ids.count(item) for item in ids}
            for key, value in sorted(my_dict.items(), key=lambda kv: kv[1], reverse=True):
                sorted_ids.append(key)
            products_filtered = sorted(best_sellers, key= lambda x: sorted_ids.index(x['id']))
            unique_products = list({ each['id'] : each for each in products_filtered}.values()) 
            sorted_products = []
            for i in unique_products[:15]:
                sorted_products.append(i)
            offer = http.request.env['product.template'].sudo().search(['&',("offer","=",True),("detailed_type","=","product")],limit=10)
            offers = []
            for o in offer:
                offers.append({
                    "id":o.id,
                    "name":o.name,
                    'category':o.categ_id.name,
                    'is_on_sale':o.sale,
                    'regular_price':o.list_price,
                    'new_price':o.vip_price if o.vip == True else o.sale_price if o.sale == True else 0.0,
                    "image":('data:image/png;base64,'+(o.image_1920).decode("UTF-8")) if (o.image_1920) else ""
                }) 
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"services":services,"categories":categories,"vip_products":vip_products,"brands":brands,"bundles":bundles,"challenges":challenges,"hot_deals":hot_deals,"best_selling":sorted_products,"offers":offers}}),headers=headers)
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers)

    ### Hot Deals   
    @http.route('/api/hotDeals',auth="public",type="http",csrf=False,methods=["POST"])
    def hot_deals (self,**kw):
        try:
            products_list = []
            product_name = ""
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                    page_number = value['page']
                    if (value.get("name")):
                        product_name = value.get("name")
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("hot_deal","=",True),('detailed_type', '=', 'product')],limit=per_page,offset=offset)
            total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("hot_deal","=",True),('detailed_type', '=', 'product')])
            total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            pagination ={}
            for product in products:
                products_list.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                "page":page_number if page_number > 0 else 1,
                "size":0 if len(products_list) == [] else len(products_list),
                "total_pages":total_pages
            }
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,"result":{"products":products_list,"pagination":pagination}}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers={'content-type':'application/json'})

    ### Offers
    @http.route('/api/offers',auth="public",type="http",csrf=False,methods=["POST"])
    def offers (self,**kw):
        try:
            products_list = []
            product_name = ""
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                    page_number = value['page']
                    if (value.get("name")):
                        product_name = value.get("name")
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("offer","=",True),('detailed_type', '=', 'product')],limit=per_page,offset=offset)
            total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("offer","=",True),('detailed_type', '=', 'product')])
            total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            pagination ={}
            for product in products:
                products_list.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                "page":page_number if page_number > 0 else 1,
                "size":0 if len(products_list) == [] else len(products_list),
                "total_pages":total_pages
            }
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,"result":{"products":products_list,"pagination":pagination}}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers={'content-type':'application/json'})

    ### VIP
    @http.route('/api/vip',auth="public",type="http",csrf=False,methods=["POST"])
    def vip (self,**kw):
        try:
            products_list = []
            product_name = ""
            page_number = 0
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                    page_number = value['page']
                    if (value.get("name")):
                        product_name = value.get("name")
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("vip","=",True),('detailed_type', '=', 'product')],limit=per_page,offset=offset)
            total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("vip","=",True),('detailed_type', '=', 'product')])
            total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            pagination ={}
            for product in products:
                products_list.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    'image':('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                "page":page_number if page_number > 0 else 1,
                "size":0 if len(products_list) == [] else len(products_list),
                "total_pages":total_pages
            }
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,"result":{"products":products_list,"pagination":pagination}}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers={'content-type':'application/json'})

    ### best
    @http.route('/api/bestSelling',auth="public",type="http",csrf=False,methods=["GET"])
    def best_selling (self,**kw):
        try:
            best_sell = http.request.env['sale.order.line'].sudo().search([('product_id.product_tmpl_id.detailed_type','ilike','product')]) 
            best_sellers = []
            for product in best_sell:
                best_sellers.append({
                    'id':product.product_id.product_tmpl_id.id,
                    'name':product.product_id.product_tmpl_id.name,
                    'is_vip':product.product_id.product_tmpl_id.vip,
                    'is_on_sale':product.product_id.product_tmpl_id.sale,
                    'regular_price':product.product_id.product_tmpl_id.list_price,
                    'new_price':product.product_id.product_tmpl_id.vip_price if product.product_id.product_tmpl_id.vip == True else product.product_id.product_tmpl_id.sale_price if product.product_id.product_tmpl_id.sale == True else 0.0,
                    'category':product.product_id.product_tmpl_id.categ_id.name,
                    'image':('data:image/png;base64,'+(product.product_id.product_tmpl_id.image_1920).decode("UTF-8")) if product.product_id.product_tmpl_id.image_1920 != False else ""
                })
            ids = []
            sorted_ids = []
            for i in best_sellers:
                ids.append(i['id'])
            my_dict = {item: ids.count(item) for item in ids}
            for key, value in sorted(my_dict.items(), key=lambda kv: kv[1], reverse=True):
                sorted_ids.append(key)
            products_filtered = sorted(best_sellers, key= lambda x: sorted_ids.index(x['id']))
            unique_products = list({ each['id'] : each for each in products_filtered}.values()) 
            sorted_products = []
            for i in unique_products[:15]:
                sorted_products.append(i)
            if sorted_products:
                return http.Response(json.dumps({'jsonrpc':'2.0','id':None,"result":sorted_products}),headers = {'content-type':'application/json'})
            else:
                return http.Response(json.dumps({'jsonrpc':'2.0','id':None,"result":[]}),headers = {'content-type':'application/json'})
        except Exception as e:
            return http.Response(json.dumps({'jsonrpc':'2.0','id':None,'error':str(e)}),headers={'content-type':'application/json'})

    ### Search Products
    @http.route('/api/searchCompare', auth='public',type='http',csrf=False,methods=['POST'])
    def search_compare(self,**kw):
        try:
            product_name = ""
            json_object = json.loads(http.request.httprequest.data)
            for key,value in json_object.items():
                product_name = value['name']
            products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type",'=',"product")])
            product_details = []
            for product in products:
                product_details.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    "image":('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":product_details}),headers = {'content-type':'application/json'}) 
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 

    ### subscribe to vip 
    @http.route('/api/subscribe', auth='none',type='http',csrf=False,website=False,methods=['POST'])
    def subscribe_to_vip(self,**kw):
        try:
            if (http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id',"=",http.request.session.uid)])
                product_with_vip = http.request.env['cart'].sudo().search(['&',('partner_id.id','=',user.partner_id.id),("product_id.name",'ilike',"vip charge")])
                vip_charge = http.request.env['product.template'].sudo().search([('name','ilike','vip charge')])
                if user.partner_id.is_vip != True:
                    if product_with_vip:
                        return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Subscription Charge Already in Cart "}), headers={'content-type':'application/json'})
                    else:
                        partner = http.request.env['res.partner'].sudo().search([('parent_id.id','=',user.partner_id.id)]).ids
                        orders = http.request.env['stock.picking'].sudo().search(["&",('state','!=','cancel'),"|",("partner_id.id",'=',user.partner_id.id),('partner_id.id','in',partner)]) 
                        canceled_orders = http.request.env['stock.picking'].sudo().search(["&",('state','ilike','cancel'),"|",("partner_id.id",'=',user.partner_id.id),('partner_id.id','in',partner)]) 
                        can_add_vip = False
                        products = []
                        print (canceled_orders)
                        print(orders)
                        if canceled_orders and not orders:
                                can_add_vip = True
                        elif not canceled_orders and orders:
                            for o in orders:
                                order_line = http.request.env['sale.order.line'].sudo().search([('order_id.name','=',o.origin)])
                                for ol in order_line:
                                    products.append(ol.name)
                                    if "vip charge" in products:
                                        can_add_vip = False
                                    else:
                                        can_add_vip = True
                        elif canceled_orders and orders:
                            for o in orders:
                                order_line = http.request.env['sale.order.line'].sudo().search([('order_id.name','=',o.origin)])
                                for ol in order_line:
                                    products.append(ol.name)
                                    if "vip charge" in products:
                                        can_add_vip = False
                                    else:
                                        can_add_vip = True
                        else:
                                can_add_vip = True
                        print (products)    
                        print (can_add_vip)
                        if (can_add_vip == True):
                            http.request.env['cart'].with_user(user.id).create({
                                    'partner_id': user.partner_id.id,
                                    'product_id': vip_charge.id,
                                    "quantity":1,
                                })
                        else:
                            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Sorry, You cant add VIP Charge right now"}}), headers={'content-type':'application/json'})
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Successfully Added Subscription Charge to Cart"}}), headers={'content-type':'application/json'})
                else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"status":"Sorry, You are already a VIP member"}}), headers={'content-type':'application/json'})
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}), headers={'content-type':'application/json'})
        except Exception as e:
                 return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}), headers={'content-type':'application/json'})

    ### Get Filter Options
    @http.route('/api/getFilterOptions', auth='public',type='http',csrf=False,methods=['GET'])
    def get_filter_options(self,**kw):
        try:
            categories = []
            brands = []
            brand = http.request.env['product.attribute'].sudo().search([('name','=',"Brand")])
            for brand in brand:
                brand_values = http.request.env['product.attribute.value'].sudo().search([('attribute_id.id','=',brand.id)])
                for b in brand_values:
                    brands.append({
                        "id":b.id,
                        "name":b.name,
                    })
            category = http.request.env['product.category'].sudo().search([('parent_id.id',"!=",1)])
            categories = []
            for cat in category:
                if cat.parent_id.id != False:
                    categories.append({
                        "id":cat.id,
                        "name":cat.name,
                    })
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"categories":categories,"brands":brands}}),headers = {'content-type':'application/json'}) 
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 

    ### Filter
    @http.route('/api/filter', auth='public',type='http',csrf=False,methods=['POST'])
    def filter(self,**kw):
        try:
            brand = None
            category = None
            max = 0
            condition = ""
            page_number = 0
            product_name = ""
            json_objectt = json.loads(http.request.httprequest.data)
            for key,value in json_objectt.items():
                page_number = value['page']
                if(value.get('category_id')):
                    category = value.get('category_id')
                if(value.get('brand_id')):
                    brand = value.get('brand_id')
                if(value.get('max_price')):
                    max = value.get('max_price')
                if(value.get('condition')):
                    condition = value.get('condition')    
                if(value.get('name')):
                    product_name = value.get('name')
            per_page = 15
            offset = 0 if page_number <= 1 else (page_number - 1) * per_page
            brand_values = http.request.env['product.template.attribute.value'].sudo().search(['&',('product_attribute_value_id.id','=',brand),('attribute_id.name','=',"Brand")])
            brands = []
            for b in brand_values:
                brands.append(b.product_tmpl_id.id)
            conditions = http.request.env['product.template.attribute.value'].sudo().search(['&',('product_attribute_value_id.name','ilike',condition),('attribute_id.name','=',"Condition")])
            conditionss = []
            for c in conditions:
                conditionss.append(c.product_tmpl_id.id)
            if (brand == None and category == None and condition == ""):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product")])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            elif (category != None and brand == None and condition == ""):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("categ_id.id",'=',category)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("categ_id.id",'=',category)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            elif(brand != None and condition == "" and category == None ):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("id","in",brands)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("id","in",brands)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            elif(condition != "" and brand == None and category == None):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("id","in",conditionss)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("id","in",conditionss)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            elif(condition != "" and brand != None and category == None):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("id","in",brands),("id","in",conditionss)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("id","in",brands),("id","in",conditionss)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            elif(condition == "" and brand != None and category != None):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("categ_id.id","=",category),("id","in",brands)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("categ_id.id","=",category),("id","in",brands)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page) 
            elif(condition != "" and brand == None and category != None):
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("categ_id.id","=",category),("id","in",conditionss)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("categ_id.id","=",category),("id","in",conditionss)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            else:
                products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),("detailed_type","=","product"),('list_price','<=',max),("categ_id.id","=",category),("id","in",brands),("id","in",conditionss)],limit=per_page,offset=offset)
                total_products = http.request.env['product.template'].sudo().search(['&',("name".lower(),'ilike',product_name.lower()),('list_price','<=',max),("detailed_type","=","product"),("categ_id.id","=",category),("id","in",brands),("id","in",conditionss)])
                total_pages = 1 if math.ceil(len(total_products)/per_page) <= 1 else math.ceil(len(total_products)/per_page)
            product_details = []                
            for product in products:
                product_details.append({
                    'id':product.id,
                    'name':product.name,
                    'is_vip':product.vip,
                    'is_on_sale':product.sale,
                    'regular_price':product.list_price,
                    'new_price':product.vip_price if product.vip == True else product.sale_price if product.sale == True else 0.0,
                    'category':product.categ_id.name,
                    "image":('data:image/png;base64,'+(product.image_1920).decode("UTF-8")) if product.image_1920 != False else ""
                })
            pagination = {
                "page":page_number if page_number > 0 else 1,
                "size":0 if len(product_details) == [] else len(product_details),
                "total_pages":total_pages
            }
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"products":product_details,"pagination":pagination}}),headers = {'content-type':'application/json'}) 
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers = {'content-type':'application/json'}) 

    ### check Vip Expire
    @http.route('/api/checkVip', auth='none',type='http',csrf=False,website=False,methods=['GET'])
    def check_vip(self):
        headers = {'content-type':'application/json'}
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                vip = http.request.env['vip.subscribe'].sudo().search([("subscriber_id.id",'=',user.partner_id.id)])
                if vip:
                    for v in vip:
                        if v.end_date < datetime.date.today():
                            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"is_vip":False}}),headers=headers)     
                        else:
                            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"is_vip":True}}),headers=headers)     
                else:
                    return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":{"is_vip":False}}),headers=headers)     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers) 

    ### Vip Details
    @http.route('/api/vipInfo', auth='none',type='http',csrf=False,website=False,methods=['GET'])
    def vip_info(self):
        headers = {'content-type':'application/json'}
        try:
            if(http.request.session.uid != None):
                user = http.request.env['res.users'].sudo().search([('id','=',http.request.session.uid)])
                vip = http.request.env['vip.subscribe'].sudo().search([("subscriber_id.id",'=',user.partner_id.id)])
                subscriber = {}
                for s in vip:
                    subscriber = {
                        "subscription_date":str(s.start_date.strftime("%d-%m-%Y")),
                        "expiration_date":str(s.end_date.strftime("%d-%m-%Y")),
                        "cost":int(s.cost)
                    }
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"result":subscriber}),headers=headers)                     
            else:
                return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":"Session expired"}),headers=headers)     
        except Exception as e:
            return http.Response(json.dumps({"jsonrpc":"2.0","id":None,"error":str(e)}),headers=headers) 
    