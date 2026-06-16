import packageJson from '../../package.json';
import GitHubIcon from '@mui/icons-material/GitHub';
import { Button, Dialog, DialogActions, DialogContent, DialogContentText, Link, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

export function AboutDialog({ open, onClose }: Readonly<{ open: boolean, onClose?: () => void }>) {
    const { t } = useTranslation();
    return (
        <Dialog open={open} onClose={onClose} aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description">
            <DialogContent>
                <DialogContentText component="div">
                    <Typography variant="h6" gutterBottom>
                        {t('about.title', { version: packageJson.version })}
                    </Typography>
                    <Typography variant="body1">{t('about.body')}</Typography>
                    <Link title="GitHub" href="https://github.com/aminekun90/aladhan_api" sx={{ color: "inherit" }}>
                        <GitHubIcon />
                    </Link>
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" color="primary" onClick={onClose} autoFocus>
                    {t('about.close')}
                </Button>
            </DialogActions>
        </Dialog>
    );
}
