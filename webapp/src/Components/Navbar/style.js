import styled,{ css } from "styled-components";
import { Link } from 'react-router-dom';

export const StyledNavbar = styled.nav`
display: flex;
align-items: center;
justify-content: flex-end;
width: 100%;
height: 70px;
padding: 0 16px;
color: #ffffff;
background-color: #202023;
box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1), 0 1px2px 0 rgba(0, 0, 0, 0.06);
`;

export const NavItemLink = styled(Link)`
color: inherit;
margin-left: 16px;
${props => props.fill && css`
    background-color: #2f8bfd;
    padding: 8px 16px;
    border-radius: 4px;
    transition: background-color 0.2s;
    &:hover { background-color: #0072ff; }
`};
`;

