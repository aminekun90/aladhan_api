import GitHubIcon from '@mui/icons-material/GitHub';
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Link, Typography } from "@mui/material";
export function AboutDialog({ open, onClose }: Readonly<{ open: boolean, onClose?: () => void }>) {
    return (
        <Dialog open={open} onClose={onClose} aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description">
            <DialogTitle>About Aladhan-pi beta 0.1.0</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    <Typography variant='body1' >
                        Aladhan-pi is an open-source Python / React project that provides accurate Islamic prayer times and Qibla* direction using data from the Aladhan API.
                        It is designed to be lightweight and easy to use, making it ideal for personal use or integration into other applications.
                        The project is maintained by a community of developers and is available on GitHub for anyone to Contribute/Donate or Report issues.
                    </Typography>

                    <Link title='' href="https://github.com/aminekun90/aladhan_api" sx={{ color: "inherit" }}><GitHubIcon /></Link>

                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" color="primary" onClick={onClose} autoFocus>
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    );
}