class Get_payload_to_create:
    
    def __init__(self, asset_tag, status_id, model_id, name, serial):
        self.asset_tag = asset_tag
        self.status_id = status_id
        self.model_id = model_id
        self.name = name
        self.serial = serial

    def to_dict(self):
        return vars(self)


class Get_payload_to_modify:

   def __init__(self, asset_tag, notes, status_id, model_id, warranty_months, purchase_cost, order_number, name, _snipeit_mac_address_1, company_id):
       self.asset_tag = asset_tag
       self.notes = notes
       self.status_id = status_id
       self.model_id = model_id
       self.warranty_months = warranty_months
       self.purchase_cost = purchase_cost
       self.order_number = order_number
       self.name = name
       self._snipeit_mac_address_1 = _snipeit_mac_address_1
       self.company_id = company_id or 1

   def to_dict(self):
       return vars(self)


class Asset_description:
    def __init__(self, name, status_id, model_id, notes, warranty_months, purchase_cost, order_number):
        self.name = name
        self.status_id = status_id
        self.model_id = model_id
        self.notes = notes
        self.warranty_months = warranty_months
        self.purchase_cost = purchase_cost
        self.order_number = order_number

    def to_dict(self):
        return vars(self)


class Asset_id:
    def __init__(self, asset_tag, serial, id, mac):
        self.asset_tag = asset_tag
        self.serial = serial
        self.id = id
        self.mac = mac

    def to_dict(self):
        return vars(self)




