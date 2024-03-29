API for Baton Data
====================

There is an API specifically for tinycloud to send readings to the Baton data database.  This could also be repurposed to handle bulk upload of readings if required.  This is accessed via /api/v1/readings/   (with an s)

The API for getting readings is accessed via /api/v1/reading/  (without an s)     

The rest of the documentation applies to the Read Only api /api/v1/reading/

Authentication - Creating a key
---------------------------------

To make a call to the api requires an API key.
A key is create for a specific user, so this user can be a real person or be created for system access, The user is created with an email address as a key, it is not used as an email address so any format will do, eg. "external_access_key@batondata.co.uk".

Having got the user email address, in admin, select API Keys, Add.

Enter the email address in the name field (there is no validation, so make sure it matches a user email address)

Click save and a bar will be displayed at the top of the screen with the api key.  This is only displayed once, so copy it now.  Note that there is a full stop at the end of the key - DO NOT INCLUDE THIS.  A valid key looks like: C4zfpP8R.nJ3Eg97WD4r07T2yu6xTuxRHHXvJs86a

Authentication - Using a key
---------------------------------

A custom tag HTTP_BAT_API_KEY is used to identify the token, so a call using a python request that adds the api to the header looks like this:

to post data to the API::

    r = requests.post(https://batondata.co.uk/api/v1/readings/, json=payload,
                              headers={'Authorization': f'HTTP_BAT_API_KEY {settings.BATON_API_KEY}'})

To get data from the API::

    r = requests.get("https://batondata.co.uk/api/v1/reading/latest/", headers={'Authorization': f'HTTP_BAT_API_KEY {settings.BATON_API_KEY}'})

See web/tests/test_api.py for examples


Filtering
----------

Filter on timestamp:

After a datetime::

    https://batondata.co.uk/api/v1/reading/?timestamp__gte=2021-08-13T15:00

Range::

    https://batondata.co.uk/api/v1/reading/?timestamp__gte=2021-08-13T15:00&timestamp__lte=2021-08-13T16:00

For a specific gadget::

    https://batondata.co.uk/api/v1/reading/?gadget_id=OPC_1

Latest reading only::

    https://batondata.co.uk/api/v1/reading/latest/