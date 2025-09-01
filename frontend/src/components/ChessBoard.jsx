import {Chessboard} from "react-chessboard"
import {Chess} from "chess.js"
import { useState,useEffect } from "react"
import api from "../api"
import "../styles/Board.css"
import { Navigate } from "react-router-dom"
function ChessBoard({gameId,user}){
    const[position, setPosition] = useState(new Chess().fen());
    const[turn,setTurn]=useState("w")

    useEffect(() => {
        if (turn !== user) {
            console.log("ai's turn");
            aiMove(position);
        } else {
            console.log("user's turn");
        }
    }, [turn]);

    useEffect(()=>{
        getLatestFen()
    },[])

    
    const changePlayerTurn=()=>{
        setTurn(turn==="w"?"b":"w")
    }

    const getLatestFen =async()=>{
            try{
                const res= await api.post("/api/get-latest-fen/",{gameId:gameId})
                if(res.status===200){
                    setPosition(res.data.fen)
                }
            }catch(error){
                alert(error)
            }
    }

    const aiMove = async(newFen)=>{
        console.log(`fen sent to ai is ${position}`)
        try{
            const res= await api.post("/api/ai-move/",{fen:newFen,gameId:gameId})
            if (res.status===200){
                setPosition(res.data.fen)
            }
        } catch(error){
            console.log(error)
        }
        changePlayerTurn()
        
    }

    const droppedPiece=({sourceSquare,targetSquare, piece})=>{
        const pieceType =  piece.pieceType
        const move={
            from:sourceSquare,
            to:targetSquare,
            promotion:"q"
        }

        const gameCopy= new Chess(position)
        const result=gameCopy.move(move)
        if(result){
            const newFen=gameCopy.fen()
            setPosition(newFen);
            handleMove(sourceSquare,targetSquare,pieceType,result.after)
        }
    }


    const handleMove= async(sourceSquare,targetSquare,pieceType,result)=>{
        try{
            const res=await api.post("/api/validate-move/",{
            source:sourceSquare,
            destination:targetSquare,
            piece:pieceType,
            fen_after_move:result,
            game:gameId
            })
            console.log(`source is ${sourceSquare}, target is ${targetSquare}, piece is ${pieceType}, result is ${result}`)

            if(res.status===201){
                console.log(`move number is ${res.data.move_number}`)
            }else{
                alert("invalid move")
            }
        }catch(error){
            console.log(error)
        }

        changePlayerTurn()
    }

    const moveOnlyYourPiece=({piece})=>{
        return piece.pieceType[0]==user
        
    }

    const isItYourTurn =()=>{
        return turn[0]===user
    }
   

    const undoMove =async()=>{
        try{
            const res= await api.post("/api/undo-move/",{gameId:gameId})
            if (res.status===200){
                setPosition(res.data.fen)
            }
        }
        catch(error){
            console.log(error)
        }
        changePlayerTurn()
    }

   
    const options={
        position,
        onPieceDrop:droppedPiece, 
        allowDragging:isItYourTurn,
        canDragPiece:moveOnlyYourPiece
    }

    return (
        <div  className="flex justify-center items-center p-6">
            <div id="board-container">
                <Chessboard
                options={options}
            />
                <button 
                className="h-10 px-5 m-2 text-indigo-100 transition-colors duration-150 bg-indigo-700 rounded-lg hover:bg-indigo-800 h-12 px-6 m-2 text-lg"
                onClick={undoMove}>undo move</button>
            </div>
        </div>
    )

}

export default ChessBoard