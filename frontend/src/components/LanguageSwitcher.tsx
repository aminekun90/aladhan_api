import { LANGUAGES } from "@/i18n";
import LanguageIcon from "@mui/icons-material/Language";
import { Box, IconButton, ListItemText, Menu, MenuItem, Tooltip } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export function LanguageSwitcher() {
    const { t, i18n } = useTranslation();
    const [anchor, setAnchor] = useState<null | HTMLElement>(null);
    const current = i18n.resolvedLanguage;

    return (
        <>
            <Tooltip title={t("nav.language")}>
                <IconButton onClick={(e) => setAnchor(e.currentTarget)} aria-label={t("nav.language")}>
                    <LanguageIcon />
                </IconButton>
            </Tooltip>
            <Menu anchorEl={anchor} open={!!anchor} onClose={() => setAnchor(null)}>
                {LANGUAGES.map((lang) => (
                    <MenuItem
                        key={lang.code}
                        selected={lang.code === current}
                        onClick={() => { i18n.changeLanguage(lang.code); setAnchor(null); }}
                    >
                        <Box component="span" sx={{ marginInlineEnd: 1.25 }}>{lang.flag}</Box>
                        <ListItemText primary={lang.label} />
                    </MenuItem>
                ))}
            </Menu>
        </>
    );
}
