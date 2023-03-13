import Button from 'react-bootstrap/Button';
import '../styles/Admin.css';

const Admin = () => {
    return (
        <>
        <head>
        <p>Admin Page</p>
        </head>
            <body>
                <form>
                <div>
                    <div>
                        <label>RSS-feed</label>
                        <input type='text'/>
                        <br/>
                        <button className='button button1'>add</button>
                        <button className='button button2'>remove</button>
                    </div>
                    <div>
                        <label>Xml-xpaths</label>
                        <input type='text'/>
                        <br/>
                        <button className='button button1'>add</button>
                    </div>  
                    <div>
                        <label>Admin</label>
                        <input type='text'/>
                        <br/>
                        <button className='button button1'>add</button>                   
                    </div>
                </div>            
            </form>
            </body>
        </>
    );
};

export default Admin;
