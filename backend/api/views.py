from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Game,Move
from .serializers import UserSerializer,GameSerializer,MoveSerializer
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.core.exceptions import ObjectDoesNotExist
import chess,math

class CreateUserView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    permission_classes=[AllowAny]

class CreateGame(generics.CreateAPIView):
    queryset=Game.objects.all()
    serializer_class=GameSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(player=self.request.user)

class CreateMove(generics.CreateAPIView):
    queryset=Move.objects.all()
    serializer_class=MoveSerializer
    permission_classes=[IsAuthenticated]

class UndoMove(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        gameId=request.data.get('gameId')
        try:
            game=Game.objects.all().get(id=gameId)
        except Game.DoesNotExist:
            return Response({"error: game not found"},status=status.HTTP_404_NOT_FOUND)
        
        move=game.moves.order_by("move_number")
        if not move.exists():
            return Response({"error: no move left"},status=status.HTTP_400_BAD_REQUEST)
        
        moves = game.moves.order_by('move_number')

        last_move = moves.last()
        last_move.delete()

        moves = game.moves.order_by('move_number')

        if moves.exists():
            new_fen = moves.last().fen_after_move
        else:
            new_fen = game.initial_fen
        
        return Response({"fen":new_fen},status=status.HTTP_200_OK)


class AIMove(APIView):
    piece_values={
        chess.PAWN:1,
        chess.BISHOP:3,
        chess.KNIGHT:3,
        chess.QUEEN:9,
        chess.ROOK:5
    }

    def evaluate_board(self,board):
        if board.is_checkmate():
            return -999999 if board.turn==chess.WHITE else 999999
        if board.is_game_over():
            return 0    
        
        white=black=0
        for square,piece in board.piece_map().items():
            if piece.piece_type != chess.KING:
                value=AIMove.piece_values.get(piece.piece_type,0)
                if piece.color==chess.WHITE:
                    white+=value
                else:
                    black-=value
        return white-black

    def minimax(self,board,depth,alpha,beta,is_maximising):
        if depth==0 or board.is_game_over():
            return self.evaluate_board(board)

        if is_maximising:
            max_eval=-math.inf
            for move in board.legal_moves:
                board.push(move)
                eval_val=self.minimax(board,depth-1,alpha,beta,False)
                board.pop()
                max_eval=max(max_eval,eval_val)
                alpha=max(alpha,eval_val)
                if beta<=alpha:
                    break
            return max_eval
        else:
            min_eval=math.inf
            for move in board.legal_moves:
                board.push(move)
                eval_val=self.minimax(board,depth-1,alpha,beta,True)
                board.pop()
                min_eval=min(min_eval,eval_val)
                beta=min(beta,eval_val)
                if beta<=alpha:
                    break
            return min_eval
    
    

    def get_best_move(self,board,depth):
        is_maximising_player=board.turn==chess.WHITE
        best_value=-math.inf if is_maximising_player else math.inf
        best_move=None
        alpha=-math.inf
        beta=math.inf

        for move in list(board.legal_moves):
            board.push(move)
            value=self.minimax(board,depth-1,alpha,beta,not is_maximising_player)
            board.pop()

            if is_maximising_player:
                if value>best_value:
                    best_value=value
                    best_move=move
                alpha=max(alpha,value)
            else:
                if value<best_value:
                    best_value=value
                    best_move=move
                beta=min(beta,value)

            if beta<=alpha:
                break
        return best_move
    
    def post(self,request):
        DEPTH=3
        
        try:
            initial_fen=request.data.get('fen')
            gameId=request.data.get('gameId')

            if not initial_fen or not gameId:
                return Response({"error": "missing gameId or fen"},status=status.HTTP_400_BAD_REQUEST)

            #set up board, find best move
            board=chess.Board(initial_fen)
            print(f"board fen is {str(board.fen)}")
            best_move=self.get_best_move(board,DEPTH)
            
            if best_move is None:
                return Response({"error": "no legal moves"})
            
            #get piece details
            piece_info=board.piece_at(best_move.from_square)
            color="w" if piece_info.color==chess.WHITE else "b"
            symbol=piece_info.symbol()
            piece=color+symbol

            #get fen after move
            board.push(best_move)
            fen_after_move=board.fen()
            board.pop()


            #save ai move to database
            try:
                game=Game.objects.get(id=gameId)
                move_data={
                    'game':gameId,
                    'source':chess.square_name(best_move.from_square),
                    'destination':chess.square_name(best_move.to_square),
                    'piece':piece,
                    'fen_after_move':fen_after_move
                }

                serializer=MoveSerializer(data=move_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except ObjectDoesNotExist:
                return Response({"error": "invalid game_id"}, status=status.HTTP_400_BAD_REQUEST)


            return Response({
                "fen":fen_after_move         
                },
                status.HTTP_200_OK)
        

        except ValueError:
            return Response({"error":"invalid FEN or gameId"},status=status.HTTP_400_BAD_REQUEST)
