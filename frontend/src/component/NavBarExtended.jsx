import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { deleteCookie, getCookie } from '../js/Methods'
import Chat from './Chat'
import { API } from ".."

export default function NavBarExtended({setIsOpen}) {
    const navigate = useNavigate()
    const location = useLocation()
    const [chatList, setChatList] = useState([])
    const [search, setSearch] = useState("")

    useEffect(() => {
        fetch(`${API}chats/get-history?username=${getCookie("username")}`).then(
            response => {
                if (response.status === 200) {
                    return response.json()
                }

                return Promise.reject(response)
            }
        ).then(data => {
            setChatList(data)
        }).catch(response => {
            console.log(response)
        })
    }, []) 

    function logoutHandler(event) {
        deleteCookie("username")
        deleteCookie("role")
        navigate("../login")
    }

    function newChatHandler(event) {
        event.stopPropagation()
        if (location.pathname !== "./chat/newchat") {
            navigate("./newchat")
            setIsOpen(false)
            return
        }

        return
    }

    function onChangeHandler(event) {
        event.preventDefault()
        setSearch(event.target.value)
    }

    function onKeyDownHandler(event) {
        if (event.key === 'Enter') {
            fetch(`${API}chats/search?username=${getCookie("username")}&search_string=${search}`).then(
                response => {
                    if (response.status === 200) {
                        return response.json()
                    }

                    return Promise.reject(response)
                }
            ).then(data => {
                console.log(data)
                setChatList(data)
            }).catch(response => {
                console.log(response)
            })
        }
    }

    return (
        <div className="h-[100%] w-[22%] bg-dark-gray p-[1vw] flex flex-col"
            onClick={(e) => e.stopPropagation()}>

            <div className="w-[100%] h-[3.3vw] gradient text-[1.3vw] rounded-lg flex justify-center items-center text-white font-[600] cursor-pointer"
                onClick={(e) => newChatHandler(e)}>
                New Chat
            </div>
            <div className="w-full h-[0.3vw] my-[1vw] bg-gray" />
            <input className="w-full h-[3.1vw] bg-dim-gray rounded-lg text-input px-[0.5vw] text-[1.1vw] text-white" placeholder="Search"
                    name="search"
                    value={search}
                    onChange={(e) => onChangeHandler(e)}
                    onKeyDown={(e) => onKeyDownHandler(e)} />
            <div className="w-full flex-1 max-h-[55%] mt-[1.5vw] text-white font-[500] text-[1.2vw] overflow-y-scroll scrollbar-hidden">
                {chatList.map((chat, index) => (
                    <Chat key={index} chat={chat} setIsOpen={setIsOpen} />
                ))}
            </div>

            <div className="flex flex-col gap-[1vw] mt-auto">
                <div className="w-full h-[0.3vw] bg-gray" />
                <div className="w-full h-fit text-[1.3vw] text-white flex flex-col">
                    <p><b>Username:</b> {getCookie("username")}</p>
                    <p><b>Role:</b> {getCookie("role")}</p>
                </div>
                <div className="w-full h-[0.3vw] bg-gray" />
                <div className="w-[100%] h-[3.3vw] bg-red-600 text-[1.3vw] rounded-lg flex justify-center items-center text-white font-[600] cursor-pointer"
                    onClick={(e) => logoutHandler(e)}>
                    Log Out
                </div>
            </div> 
        </div>
    )
}