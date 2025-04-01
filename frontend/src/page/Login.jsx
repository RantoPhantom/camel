import { useRef, useState } from "react"
import { setCookie } from "../js/Methods"
import { useNavigate } from 'react-router-dom'
import { API } from ".."

export default function Login() {
    const usernameField = useRef()
    const passwordField = useRef()
    const navigate = useNavigate()
    const [errorMsg, setErrorMsg] = useState("")
    const [formData, setFormData] = useState({
        username: "",
        password: ""
    })

    function onKeyUpHandler(event) {
        event.preventDefault()
        if (event.key === "Enter") {
            if (document.activeElement === usernameField.current) {
                passwordField.current.focus()
                return
            }

            if (document.activeElement === passwordField.current) {
                loginHandler(event)
                return
            }
        }
    }
    
    function onChangeHandler(event) {
        const {name, value} = event.target
        setFormData((prevData) => (
            {
                ...prevData,
                [name]: value
            }
        ))
    }

    function loginHandler(event) {
        event.preventDefault()
        if (formData.username.length < 1) {
            setErrorMsg("Please enter username.")
            return
        }

        if (formData.password.length < 1) {
            setErrorMsg("Please enter password.")
            return
        }

        fetch(`${API}auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        }).then(response => {
            if (response.status === 200) {
                return response.json()
            }

            return Promise.reject()
        }).then(data => {
            setCookie("username", data.username, 1)
            setCookie("role", data.role, 1)
            setErrorMsg("")
            navigate("../chat")
        }).catch(response => {
            console.log(response)
            setErrorMsg("Wrong username or password. Please try again!")
        })
    }

    return (
        <div className="w-[100vw] h-[100vh] relative text-white">
            <div className="w-fit h-fit bg-dark-gray absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] rounded-lg box-border px-[2vw] py-[1vw] flex flex-col">
                <div className="text-[1.8vw] font-[600] mx-auto py-[0.8vw]">
                    Log In
                </div>
                <div className="flex flex-col gap-[0.5vw] mt-[1vw]">
                    <div className="text-[1.1vw] font-[500]">
                        Username:
                    </div>
                    <input type="text" 
                        className="text-[1.2vw] w-[22vw] py-[0.2vw] px-[0.5vw] bg-gray rounded-md text-input"
                        name="username"
                        value={formData.username}
                        onChange={(e) => onChangeHandler(e)}
                        onKeyUp={(e) => onKeyUpHandler(e)}
                        ref={usernameField}
                        required></input>
                </div>
                <div className="flex flex-col gap-[0.5vw] mt-[1vw]">
                    <div className="text-[1.1vw] font-[500]">
                        Password:
                    </div>
                    <input type="password" 
                        className="text-[1.2vw] w-[22vw] py-[0.2vw] px-[0.5vw] bg-gray rounded-md text-input" 
                        name="password"
                        value={formData.password}
                        onChange={(e) => onChangeHandler(e)}
                        onKeyUp={(e) => onKeyUpHandler(e)}
                        ref={passwordField}
                        required></input>
                </div>
                {errorMsg && (
                    <div className="text-red-500 max-w-[22vw] text-[0.9vw] mt-[0.5vw]">
                        {errorMsg}
                    </div>
                )}
                
                <div className="flex justify-center mt-[1.5vw] text-[1vw]">
                    <p>Don't have an account? <a href="./signup" className="underline text-blue-300">Sign Up</a></p>
                </div>
                <div className="w-full gradient text-[1.5vw] font-[600] text-center mt-[5vw] py-[0.4vw] rounded-lg mb-[1vw] cursor-pointer"
                    onClick={(e) => loginHandler(e)}>
                    Log In
                </div>
            </div>
        </div>
    )
}