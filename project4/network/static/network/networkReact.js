function TextApp(props) {
    
    const [state, setState] = React.useState({
        button: 'Edit',
        element: 'div',
        text: props.text
    })

    function element() {
        if (state.element === 'textarea') {
            return (
                <textarea value={state.text} onChange={updateText} class="form-control"></textarea>
            )
        } else {
            return (
                <div>{state.text}</div>
            )
        }
    }

    function updateText(event) {
        setState({
            ...state,
            text: event.target.value
        })
    }
            
    function editButton() {    
        if (state.button === 'Edit') {
            
            setState({
                ...state,
                element: 'textarea',
                button: 'Save'
            })

        // if button === 'save'
        } else {
            fetch('/edit', {
                method: 'PUT',
                body: JSON.stringify({
                    post: props.id,
                    text: state.text
                })
            })
            setState({
                ...state,
                element: 'div',
                button: 'Edit'
            })
        }
    }
    
    return (
        <div>    
            {element()}
            <a href="#" onClick={editButton}>{state.button}</a>
        </div>
    ) 
}

function LikesApp(props) {
    // turn props.liked into bool
    const liked = (props.liked === "True")
    
    // function to set initial button
    function setButton() {
        if (liked === true) {
            return('unlike')
        
        } else {
            return('like')
        }
    }
    
    const button = setButton();
    const [state, setState] = React.useState({
        button: button,
        likes: parseInt(props.likes),
        liked: liked
    });
    
    function editLikes() {
        console.log(state.liked)
        if (state.liked === false) {
            fetch('/like', {
                method: 'PUT',
                body: JSON.stringify({
                    post: props.id,
                    action: 'like'
                })
            })
            setState({
                ...state,
                likes: state.likes + 1,
                liked: true,
                button: 'unlike'
            })
        } else {
            fetch('/like', {
                method: 'PUT',
                body: JSON.stringify({
                    post: props.id,
                    action: 'unlike'
                })
            })
            setState({
                ...state,
                likes: state.likes - 1,
                liked: false,
                button: 'like'
            })
        }
    }

    return (
        <div>
            <div>❤️{state.likes}</div>
            <button className="btn btn-primary" onClick={editLikes}>{state.button}</button>
        </div>
    )
}

document.querySelectorAll('.edit').forEach(function(div) {
    ReactDOM.render(<TextApp text={div.dataset.text} id={div.dataset.id} />, div); 
})

document.querySelectorAll('.edit-likes').forEach(function(div) {
    ReactDOM.render(<LikesApp likes={div.dataset.likes} id={div.dataset.id} liked={div.dataset.liked}/>, div);
})
