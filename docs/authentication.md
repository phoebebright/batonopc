Authentication
====================

As there will be a small number of users and the security requirement is not high, a simple token per user authentication has been implemented. All apis are also available to logged in users. 

A user is created as either staff (normal user) or as not active (access to api only).  A api only access user and token is generated for TinyCloud to be able to send data via the Import api.

All users have the same permissions in regards to the API.

Each user is given an API key generated using their email address, eg.


        self.external = CustomUser.objects.create_user("test@batondata.co.uk", 'pass')
        self.api_key, self.key = APIKey.objects.create_key(name=self.external.email)

This can also be done in admin.

The key is added to the header 