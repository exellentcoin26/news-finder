import Button from 'react-bootstrap/Button';
import '../../public/styles/Admin.css';

const Admin = () => {
    return (
        <>
            
        <p>Admin Page</p>
            <body>
                <form>
                <div>
                    <div>
                        <label>RSS-feed</label><br/>
                        <input type='text'/><br/>
                        <Button type='submit'>add</Button>
                        <Button type='submit'>remove</Button>
                    </div>
                    <div>
                        <label>Xml-xpaths</label><br/>
                        <input type='text'/><br/>
                        <Button type='submit'>add</Button>
                    </div>  
                    <div>
                        <label>Admin</label><br/>
                        <input type='text'/><br/>
                        <Button type='submit'>add</Button>                   
                    </div>
                    <div>
                        <label>username</label>
                        <input type='text'/> <br />
                    </div>
                    <div>
                        <label>password</label>
                        <input type='text' /> <br />
                        <Button>login</Button>
                    </div>
                </div>            
            </form>
            </body>
        </>
    );
};

export default Admin;
