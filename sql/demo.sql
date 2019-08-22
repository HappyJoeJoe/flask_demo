CREATE TABLE comments (
    `id` bigint primary key AUTO_INCREMENT comment '自增id',
    `account_id` bigint not null comment '账户id',
    `current_id` bigint not null comment '评论用户id',
    `refer_to_id` bigint not null comment '回复账户id',
    `comment` TEXT comment '评论',
    `status` tinyint not null comment '0:创建, 1:删除',
    `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间'
);

CREATE TABLE account (
    `id` bigint primary key AUTO_INCREMENT comment '自增id',
    `telphone` varchar(1024) not null default '' comment '手机号码',
    `nickname` varchar(32) not null default '' comment '昵称',
    `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '注册时间',
    `update_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    `last_login_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '上一次登录时间'
);