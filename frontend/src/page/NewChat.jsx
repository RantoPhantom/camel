import ChatInputBox from "../component/ChatInputBox";


export default function NewChat() {

    return (
        <div className="relative"> 
            <div className="mt-[8vw] w-[100%] text-wrap">
                <p className="text-[4vw] whitespace-pre-line font-[600] gradient-text">
                    {"Hello, Anle.\nHow can we help you?"}
                </p>
                <p className="text-[1.3vw] w-[60%] text-light-gray">
                    {"Any questions are welcome! However, questions regarding diabetes are recommended."}
                </p>
            </div>
            <div className="mt-[8vw]">
                <ChatInputBox />
            </div>
        </div>
    )
}