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
        fields=["id","created_at","initial_fen","player","player_color"]
        extra_kwargs={
            "player":{
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
    
    def validate(self, attrs):
        return attrs
    
    def create(self, validated_data):
        game=validated_data['game']
        number_of_moves=game.moves.count()+1
        validated_data['move_number']=number_of_moves
        print("fen after move is "+validated_data["fen_after_move"])
        return super().create(validated_data)