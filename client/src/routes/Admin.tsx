import Button from 'react-bootstrap/Button';

const Admin = () => {
    return (
        <>
            
        <p>Admin Page</p>
            <form>
                <div>
                    <label> RSS-feed</label><br/>
                    <input type='text'/><br/>
                    <Button type='submit'>add</Button>
                    <Button type='submit'>remove</Button>
                </div>
                <div>
                    <label> Xml xpaths</label><br/>
                    <input type='text'/><br/>
                    <Button type='submit'>add</Button>
                </div>  
                <div>
                    <label>Admin</label><br/>
                    <input type='text'/><br/>
                    <Button type='submit'>add</Button>                   
                </div>            
            </form>
        
            
            
        </>
    );
};

export default Admin;
