from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator,EmailValidator


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.TextField(max_length=50)
    email = models.EmailField(validators=[
            EmailValidator(message='Enter a valid email address.')
        ],unique=True)
    password = models.CharField(max_length=4096,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{5,}$',
                message='Password must contain atleast 1 uppercase letter, 1 special character, and 1 number and be atleast 5 characters long.',
                code='invalid_password_format'
            ),
        ])

    no_of_posts = models.IntegerField(default=0, null=True, blank=True)
    name = models.TextField(max_length=50,null=True,blank=True)
    bio = models.TextField(max_length=150,null=True,blank=True)
    def save(self, *args, **kwargs):
        if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'user'



class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='images/')
    create_time=models.DateField(auto_now_add=True,null=True)
    caption = models.TextField(max_length=400)
    tags = models.TextField(max_length=200,null=True,blank=True)
    no_of_likes=models.IntegerField(default=0,null=True)
    no_of_comments=models.IntegerField(default=0,null=True)

    class Meta:
        db_table = 'post'


class SavedCollection(models.Model):
    saved_collection_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users,on_delete=models.CASCADE)
    no_of_posts= models.IntegerField(default=0,null=True)

    class Meta:
        db_table = 'saved_collection'

class SavedItem(models.Model):
    saved_item_id = models.AutoField(primary_key=True)
    saved_collection = models.ForeignKey(SavedCollection,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)

    class Meta:
        db_table = 'saved_item'
        unique_together = ('saved_collection','post')

class LikedPost(models.Model):
    liked_post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)


    class Meta:
        db_table = 'liked_post'
        unique_together = ('user','post')
