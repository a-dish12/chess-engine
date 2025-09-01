from django.urls import path
from . import views

urlpatterns = [
    path("create-game/",views.CreateGame.as_view(),name="create-game"),
    path("validate-move/",views.CreateMove.as_view(),name="validate-move"),
    path("undo-move/",views.UndoMove.as_view(),name="undo-move"),
    path("ai-move/",views.AIMove.as_view(),name="ai-move"),
    path("get-latest-fen/",views.GetLastFEN.as_view(),name="get-latest-fen")
]
