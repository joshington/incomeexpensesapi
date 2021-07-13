from .test_setup import TestSetUp
from ..models import User


class TestViews(TestSetUp):
    def test_user_cannot_register_with_no_data(self):
        res=self.client.post(self.register_url)
        self.assertEqual(res.status_code,400) 
        #this is to ensure that the user cant register by just clicking on the button

    def test_user_can_register_correctly(self):
        res=self.client.post(self.register_url,self.user_data,format="json")
        # import pdb
        # pdb.set_trace()
        self.assertEqual(res.data['email'],self.user_data['email'])
        self.assertEqual(res.data['username'],self.user_data['username'])
        #above makes sure that server can send us back the email once we create an account.
        self.assertEqual(res.status_code, 201)#use 201 since user will get created

    def test_user_cannot_login_with_unverified_email(self):
        self.client.post(self.register_url,self.user_data,format="json")
        #to login one must have registered first 
        res=self.client.post(self.login_url,self.user_data,format="json")
        self.assertEqual(res.status_code,401)

    def test_user_can_login_after_verification(self):
        response = self.client.post(self.register_url,self.user_data,format="json")
        #to login one must have registered first 
        #after registering the user we need to get back their data so that we can
        #use it
        email=response.data['email']
        user=User.objects.get(email=email)
        user.is_verified=True
        user.save()
        res=self.client.post(self.login_url,self.user_data,format="json")
        self.assertEqual(res.status_code,200)
        #have used 200 status code because i expect user to be able to login