

export default function ChatInputBox() {

    return (
        <div className="w-[100%] h-[13vw] bg-dark-gray rounded-2xl box-border px-[1.5vw] pt-[1vw] pb-[0.5vw] flex flex-col">
            <textarea className="w-[100%] h-[70%] bg-dark-gray resize-none scrollbar text-input text-[1.3vw]" placeholder="Ask something...">
            </textarea>
            <div className="w-[100%] h-[0.15vw] bg-gray"/>
            <div className="w-[100%] flex-1 flex justify-between">
                <div className="my-auto text-[1.2vw] text-light-gray flex gap-[0.2vw]">
                    <i className="ri-attachment-2"></i>
                    <p>Add attachment</p>
                </div>
                <div className="w-[10%] my-[0.5vw] gradient rounded-lg relative">
                    <i className="ri-arrow-right-line text-white text-[1.8vw] absolute top-[50%] left-[50%] translate-x-[-50%] translate-y-[-50%]"></i>
                </div>
            </div>
        </div>
    )
}