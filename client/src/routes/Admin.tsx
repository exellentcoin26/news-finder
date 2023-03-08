import Button from 'react-bootstrap/Button';

const Admin = () => {
    return (
        <>
            
        <p>Login Page</p>
            <form>
                <div>
                    <label> Add RSS-feed</label><br/>
                    <input type='text'/>
                </div>
                <div>
                    <label> Xml xpaths</label><br/>
                    <input type='text'/>
                </div>  
                <div>
                    <label> Add Admin</label><br/>
                    <input type='text'/>                    
                </div>
                <div>
                    <label> Remove RSS-feed </label><br/>
                    <input type='text'/><br/>
                </div>
                    <Button>submit</Button>
            </form>
        
            
            
        </>
    );
};

export default Admin;
