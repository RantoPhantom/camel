import { useRef, useState } from "react"
import { useNavigate } from 'react-router-dom'
import { API } from ".."

export default function SignUp() {
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
                signupHandler(event)
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

    function signupHandler(event) {
        event.preventDefault()
        if (formData.username.length < 1) {
            setErrorMsg("Please enter username.")
            return
        }

        if (formData.password.length < 1) {
            setErrorMsg("Please enter password.")
            return
        }

        const userInfo = {
            username: formData.username,
            icon_file: "",
            role: "user",
            password: formData.password
        }

        fetch(`${API}auth/signup`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(userInfo)
        }).then(response => {
            if (response.status === 200) {
                return response.json()
            }

            return Promise.reject()
        }).then(() => {
            setErrorMsg("")
            navigate("../login")
        }).catch(response => {
            console.log(response)
            setErrorMsg("Account existed. Please try again!")
        })
    }
    return (
        <div className="w-[100vw] h-[100vh] relative text-white">
            <div className="w-fit h-fit bg-dark-gray absolute top-1/2 left-1/2 translate-x-[-50%] translate-y-[-50%] rounded-lg box-border px-[2vw] py-[1vw] flex flex-col">
                <div className="text-[1.8vw] font-[600] mx-auto py-[0.8vw]">
                    Sign Up
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
                    <p>Have an account already? <a href="./login" className="underline text-blue-300">Log In</a></p>
                </div>
                <div className="w-full gradient text-[1.5vw] font-[600] text-center mt-[5vw] py-[0.4vw] rounded-lg mb-[1vw] cursor-pointer"
                    onClick={(e) => signupHandler(e)}>
                    Sign Up
                </div>
            </div>
        </div>
    )
}