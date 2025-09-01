import ChessBoard from "../components/ChessBoard"
import { useState,useEffect } from "react"
import api from "../api"
import { ACCESS_TOKEN } from "../constants"
import { Chess } from "chess.js"
import "../styles/App.css"
import RadioButtons from "../components/RadioButtons"
function Home(){
    const WHITE="w"
    const INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    const[color,setColor]=useState(WHITE)
    const[game,setGame]=useState({
        id:-1,
        created:false
    })

    useEffect(()=>{
        const savedGame=localStorage.getItem("currentGame")
        if (savedGame){
            const parsed=JSON.parse(savedGame)
            setGame({id:parsed.id,created:parsed.created})
            setColor(parsed.color)
        }
    },[])


    console.log(`gameId is ${game.id}`)
    const createGame= async ()=>{
        try{
            const res= await api.post("/api/create-game/",{
                initial_fen:INITIAL_FEN,
                player_color:color
            })
            if(res.status===201){
                const newGame={id:res.data.id,created:true}
                setGame(newGame)
                localStorage.setItem("currentGame",JSON.stringify({...newGame,color}))
            }
            
        }catch(error){
            console.log(error)
        }
    }

    const handleColorChange=(e)=>{
        setColor(e.target.value)
    }

    const getColor =()=>{
        return color
    }
   
    const content=()=>{
        let cont
        
        if(game.created){
            cont=<div>
                    <ChessBoard gameId={game.id} user={color}/>
                </div>
        }else{
            cont=<div className="min-h-screen flex justify-center items-center">
                    
                    <button className="h-10 px-5 m-2 text-indigo-100 transition-colors duration-150 bg-indigo-700 rounded-lg hover:bg-indigo-800 h-12 px-6 m-2 text-lg"
                    onClick={()=>{
                    createGame()
                    }}>create new game
                    </button>
                    <RadioButtons color={getColor} handleColorChange={handleColorChange}/>
                    
                </div>
        }
        return cont
    }

    return(
        content()
    )
}
export default Home