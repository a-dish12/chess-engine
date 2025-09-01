from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    player=models.ForeignKey(User,on_delete=models.CASCADE,related_name="games")
    created_at=models.DateTimeField(auto_now_add=True)
    initial_fen=models.CharField(max_length=100,default="start")
    player_color=models.CharField(max_length=5,default="white")
    current_fen=models.CharField(max_length=100,default=initial_fen)

class Move(models.Model):
    game=models.ForeignKey(Game,on_delete=models.CASCADE,related_name="moves")
    piece=models.CharField(max_length=25)
    move_number=models.PositiveIntegerField()
    source=models.CharField(max_length=2)
    destination=models.CharField(max_length=2)
    fen_after_move=models.TextField()



    
