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


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post= models.ForeignKey(Post,on_delete=models.CASCADE)
    commented_user= models.OneToOneField(Users,on_delete=models.CASCADE)
    commented_text=models.TextField(max_length=250)

    class Meta:
        db_table = 'comment'


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



# p=Post(user=u,
#        image_url="https://imgs.search.brave.com/UU4ZeFRJ0IFPQX9uyBh5bXVhb8Z3rAGF1FxJ7ggSCfc/rs:fit:500:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTE2/NzkyMTY1Ny9waG90/by9wYW5vcmFtaWMt/YWVyaWFsLXZpZXct/b2YtZ2VybWFuLWxh/bmRzY2FwZS1yaGVp/bmdhdS10YXVudXMt/YXJlYS5qcGc_cz02/MTJ4NjEyJnc9MCZr/PTIwJmM9MkRqLVZf/YURkLVRzcEtVUFY2/WEdxY2Nial9rbGF5/VjBrRlphYi1KZmN4/TT0",
#        caption="panoramic aerial view of german landscape - rheingau-taunus area")
        # lovely #nature #scenery #2024
        
# c=Comment(post=p,commented_user=u,commented_text="Trueee !!!")
        
# INSERT INTO "main"."post" ("post_id", "image_url", "create_time", "caption", "tags", "no_of_likes", "no_of_comments", "user_id") VALUES ('1', 'https://imgs.search.brave.com/-afbGQLMisWUGlpyKoT3x2BTJAcmszX6zllYH_wypdE/rs:fit:500:0:0/g:ce/aHR0cHM6Ly9idXJz/dC5zaG9waWZ5Y2Ru/LmNvbS9waG90b3Mv/bGVuc2JhbGwteWVs/bG93LWFuZC1vcmFu/Z2UtbGlnaHRzLmpw/Zz93aWR0aD0xMDAw/JmZvcm1hdD1wanBn/JmV4aWY9MCZpcHRj/PTA', '2024-03-14', 'Darkness cannot drive out darkness: only light can do that. Hate cannot drive out hate: only love can do that.', '', '0', '1', '1');