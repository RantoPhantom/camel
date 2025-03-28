import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { useNavigate } from "react-router-dom"
import { useChatContext } from "../context/ChatContextProvider"
import { getCookie } from "../js/Methods"

const API = "http://localhost:8000/"
export default function ChatDetail() {
    const navigate = useNavigate()
    const { id } = useParams()
    const {chatState, updateMsgList, addMsg, deleteMsg, deleteNewChatMsg} = useChatContext()
    
    useEffect(() => {
        if ( !id ) {
            navigate("../newchat")
        }

        if (chatState.new_chat_msg.chat_id === Number(id) || chatState.new_chat_msg.msg_content !== "") {
            const newMsg = {
                username: getCookie("username"),
                chat_id: Number(id),
                message_content: chatState.new_chat_msg.msg_content
            }

            fetch(`${API}new-message`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(newMsg)
            }).then(response => {
                if (response.status === 200) {
                    return response.json()
                }

                return Promise.reject()
            }).then(data => {
                console.log(data)
                deleteNewChatMsg()
            }).catch(response => {
                console.log(response)
            })
        }
    })
    return(
        <div className="py-[2vw] flex flex-col" >
            <div className="flex flex-row-reverse my-[0.5vw]">
                <p className="w-fit max-w-[35vw] p-[0.8vw] rounded-2xl bg-gray font-[500] text-[1.1vw] text-justify">Lorem ipsun dolor sit amet</p>
            </div>

            <div className="w-fit h-fit my-[2.5vw]">
                <p className="w-fit h-fit font-[500] text-[1.1vw] text-justify">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent imperdiet justo at elementum egestas. Sed ut finibus nulla. Nulla faucibus sem nibh, id sollicitudin erat condimentum commodo. Donec et nibh quis est consectetur imperdiet. Phasellus at augue vel mauris tempus suscipit. Quisque rhoncus laoreet convallis. Donec non sagittis ligula. Aliquam quis ultricies lacus. Nam id augue nec massa interdum fermentum. Etiam ac augue in odio imperdiet condimentum at non nulla. Nulla at nibh tincidunt, aliquam lorem a, mattis risus.

Suspendisse vel tellus lorem. Nam erat orci, fermentum aliquet tristique sodales, condimentum quis enim. In vel nisi vel purus consequat varius. Sed ultrices bibendum suscipit. Phasellus blandit nisi ac blandit tincidunt. Praesent vitae erat ipsum. Praesent sed diam ut sapien molestie ornare. Nulla interdum ante sed laoreet efficitur. Phasellus eu bibendum metus. Nam interdum massa elit, vitae ullamcorper lorem scelerisque vel. Morbi tempus urna eu ante auctor egestas et id erat. Integer molestie non diam non tempus. Etiam risus risus, mattis in est in, tempor finibus dolor. Vivamus porta tortor pharetra metus faucibus, luctus egestas purus maximus. Sed ac lacus quis arcu rhoncus lobortis vel tristique massa. Nullam luctus eleifend neque.</p>
            </div>

            <div className="flex flex-row-reverse my-[0.5vw]">
                <p className="w-fit max-w-[35vw] p-[0.8vw] rounded-2xl bg-gray font-[500] text-[1.1vw] text-justify">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent imperdiet justo at elementum egestas. Sed ut finibus nulla. Nulla faucibus sem nibh, id sollicitudin erat condimentum commodo. Donec et nibh quis est consectetur imperdiet. Phasellus at augue vel mauris tempus suscipit. Quisque rhoncus laoreet convallis. Donec non sagittis ligula. Aliquam quis ultricies lacus. Nam id augue nec massa interdum fermentum. Etiam ac augue in odio imperdiet condimentum at non nulla. Nulla at nibh tincidunt, aliquam lorem a, mattis risus.</p>
            </div>
            
        </div>
    )
}