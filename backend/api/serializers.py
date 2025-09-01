from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Game,Move

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","username","password"]
        extra_kwargs={"password":{"write_only":True}}
    
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model=Game
        fields=["id","created_at","initial_fen","player","player_color","current_fen"]
        extra_kwargs={
            "player":{
                "read_only":True
            },
            "current_fen":{
                "read_only":True
            }
        }
    
class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model=Move
        fields="__all__"
        extra_kwargs={
            "move_number":{
                "read_only":True
            }
        }
    
    def create(self, validated_data):
        game=validated_data['game']
        validated_data['move_number']=game.moves.count()+1

        move=super().create(validated_data)
        game.current_fen=move.fen_after_move
        game.save()

        return move