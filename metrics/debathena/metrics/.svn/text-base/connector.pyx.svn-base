cdef extern from "errno.h":
    int errno

cdef extern from "stdlib.h":
    ctypedef long size_t

cdef extern from "sys/types.h":
    ctypedef long pid_t

cdef extern from "sys/socket.h":
    ctypedef long socklen_t
    struct sockaddr:
        pass

    int socket(int, int, int)
    int bind(int, sockaddr *, socklen_t)
    size_t send(int, void *, size_t, int)
    size_t recvfrom(int, void *, size_t, int, sockaddr *, socklen_t *)

    enum:
        SOCK_DGRAM
        PF_NETLINK
        AF_NETLINK

cdef extern from "linux/netlink.h":
    enum:
        NETLINK_CONNECTOR
        NLMSG_DONE
    struct sockaddr_nl:
        unsigned long nl_family
        unsigned long nl_pad
        unsigned long nl_pid
        unsigned long nl_groups
    struct nlmsghdr:
        long nlmsg_len
        long nlmsg_type
        long nlmsg_flags
        long nlmsg_seq
        long nlmsg_pid
    long NLMSG_LENGTH(long)
    void * NLMSG_DATA(void *)

cdef extern from "linux/connector.h":
    enum:
        CN_IDX_PROC
        CN_VAL_PROC
    struct cb_id:
        long idx
        long val
    struct cn_msg:
        cb_id id
        long seq
        long ack
        long len
        long flags
        char data[0]

cdef extern from "linux/cn_proc.h":
    enum proc_cn_mcast_op:
        PROC_CN_MCAST_LISTEN
        PROC_CN_MCAST_IGNORE

    enum what:
        C_PROC_EVENT_NONE "PROC_EVENT_NONE"
        C_PROC_EVENT_FORK "PROC_EVENT_FORK"
        C_PROC_EVENT_EXEC "PROC_EVENT_EXEC"
        C_PROC_EVENT_UID "PROC_EVENT_UID"
        C_PROC_EVENT_GID "PROC_EVENT_GID"
        C_PROC_EVENT_EXIT "PROC_EVENT_EXIT"

    struct ack_proc_event:
        long err
    struct fork_proc_event:
        pid_t parent_pid
        pid_t parent_tgid
        pid_t child_pid
        pid_t child_tgid
    struct exec_proc_event:
        pid_t process_pid
        pid_t process_tgid
    union id_proc_event_r:
        long ruid
        long rgid
    union id_proc_event_e:
        long euid
        long egid
    struct id_proc_event:
        pid_t process_pid
        pid_t process_tgid
        id_proc_event_r r
        id_proc_event_e e
    struct exit_proc_event:
        pid_t process_pid
        pid_t process_tgid
        long exit_code
        long exit_signal

    union event_data:
        ack_proc_event ack
        fork_proc_event fork
        exec_proc_event exec_ "exec"
        id_proc_event id_ "id"
        exit_proc_event exit_ "exit"

    struct proc_event:
        what what
        long cpu
        long timestamp_ns
        event_data event_data

cdef extern from "string.h":
    char * strerror(int)

cdef extern from "unistd.h":
    pid_t getpid()
    int close(int)


PROC_EVENT_NONE = C_PROC_EVENT_NONE
PROC_EVENT_FORK = C_PROC_EVENT_FORK
PROC_EVENT_EXEC = C_PROC_EVENT_EXEC
PROC_EVENT_UID = C_PROC_EVENT_UID
PROC_EVENT_GID = C_PROC_EVENT_GID
PROC_EVENT_EXIT = C_PROC_EVENT_EXIT


cdef class ProcEvent:
    cdef public long what
    cdef public long cpu
    cdef public long timestamp_ns


cdef class AckProcEvent(ProcEvent):
    cdef public long err

    def __repr__(self):
        return "<AckProcEvent err=%d>" % self.err


cdef class ForkProcEvent(ProcEvent):
    cdef public long parent_pid
    cdef public long parent_tgid
    cdef public long child_pid
    cdef public long child_tgid

    def __repr__(self):
        return "<ForkProcEvent ppid=%d ptgid=%d pid=%d tgid=%d>" % (
            self.parent_pid,
            self.parent_tgid,
            self.child_pid,
            self.child_tgid)


cdef class ExecProcEvent(ProcEvent):
    cdef public long process_pid
    cdef public long process_tgid

    def __repr__(self):
        return "<ExecProcEvent pid=%d tgid=%d>" % (
            self.process_pid,
            self.process_tgid)


cdef class UidProcEvent(ProcEvent):
    cdef public long process_pid
    cdef public long process_tgid
    cdef public long ruid
    cdef public long euid

    def __repr__(self):
        return "<UidProcEvent pid=%d tgid=%d ruid=%d euid=%d>" % (
            self.process_pid,
            self.process_tgid,
            self.ruid,
            self.euid)


cdef class GidProcEvent(ProcEvent):
    cdef public long process_pid
    cdef public long process_tgid
    cdef public long rgid
    cdef public long egid

    def __repr__(self):
        return "<GidProcEvent pid=%d tgid=%d rgid=%d egid=%d>" % (
            self.process_pid,
            self.process_tgid,
            self.rgid,
            self.egid)


cdef class ExitProcEvent(ProcEvent):
    cdef public long process_pid
    cdef public long process_tgid
    cdef public long exit_code
    cdef public long exit_signal

    def __repr__(self):
        return "<ExitProcEvent pid=%d tgid=%d code=%d signal=%d>" % (
            self.process_pid,
            self.process_tgid,
            self.exit_code,
            self.exit_signal)


cdef class UnknownProcEvent(ProcEvent):
    def __repr__(self):
        return "<UnknownProcEvent what=%d>" % self.what


cdef class Connector:
    cdef int sock
    cdef public object closed

    def __cinit__(self):
        self.closed = False

        cdef int flags
        cdef sockaddr_nl my_addr
        cdef char buf[4096]
        cdef nlmsghdr *nl_hdr
        cdef cn_msg *cn_hdr
        cdef proc_cn_mcast_op *mcop_msg

        self.sock = socket(PF_NETLINK, SOCK_DGRAM, NETLINK_CONNECTOR)

        my_addr.nl_family = AF_NETLINK
        my_addr.nl_groups = CN_IDX_PROC
        my_addr.nl_pid = getpid()

        if bind(self.sock, <sockaddr *>&my_addr, sizeof(my_addr)) < 0:
            raise IOError(errno, strerror(errno))

        nl_hdr = <nlmsghdr *>buf
        nl_hdr.nlmsg_len = NLMSG_LENGTH(sizeof(cn_msg) + sizeof(proc_cn_mcast_op))
        nl_hdr.nlmsg_type = NLMSG_DONE
        nl_hdr.nlmsg_flags = 0
        nl_hdr.nlmsg_seq = 0
        nl_hdr.nlmsg_pid = getpid()

        cn_hdr = <cn_msg *>NLMSG_DATA(nl_hdr)
        cn_hdr.id.idx = CN_IDX_PROC
        cn_hdr.id.val = CN_VAL_PROC
        cn_hdr.seq = 0
        cn_hdr.ack = 0
        cn_hdr.len = sizeof(proc_cn_mcast_op)

        mcop_msg = <proc_cn_mcast_op *>cn_hdr.data
        mcop_msg[0] = PROC_CN_MCAST_LISTEN

        if send(self.sock, nl_hdr, nl_hdr.nlmsg_len, 0) != nl_hdr.nlmsg_len:
            raise IOError(errno, strerror(errno))

    def __dealloc__(self):
        if not self.closed:
            close(self.sock)

    def fileno(self):
        return self.sock

    def close(self):
        if not self.closed:
            close(self.sock)
            self.closed = True

    def recv_event(self):
        cdef char buf[4096]
        cdef sockaddr_nl from_addr
        cdef socklen_t s
        cdef proc_event *ev
        cdef object ret

        from_addr.nl_family = AF_NETLINK
        from_addr.nl_groups = CN_IDX_PROC
        from_addr.nl_pid = 1
        s = sizeof(from_addr)

        if recvfrom(self.sock, buf, sizeof(buf), 0,
                    <sockaddr *>&from_addr, &s) == -1:
            raise IOError(errno, strerror(errno))

        ev = <proc_event *>((<cn_msg *>NLMSG_DATA(buf)).data)

        if ev.what == PROC_EVENT_FORK:
            ret = ForkProcEvent()
            ret.parent_pid = ev.event_data.fork.parent_pid
            ret.parent_tgid = ev.event_data.fork.parent_tgid
            ret.child_pid = ev.event_data.fork.child_pid
            ret.child_tgid = ev.event_data.fork.child_tgid
        elif ev.what == PROC_EVENT_EXEC:
            ret = ExecProcEvent()
            ret.process_pid = ev.event_data.exec_.process_pid
            ret.process_tgid = ev.event_data.exec_.process_tgid
        elif ev.what == PROC_EVENT_UID:
            ret = UidProcEvent()
            ret.process_pid = ev.event_data.id_.process_pid
            ret.process_tgid = ev.event_data.id_.process_tgid
            ret.ruid = ev.event_data.id_.r.ruid
            ret.euid = ev.event_data.id_.e.euid
        elif ev.what == PROC_EVENT_GID:
            ret = GidProcEvent()
            ret.process_pid = ev.event_data.id_.process_pid
            ret.process_tgid = ev.event_data.id_.process_tgid
            ret.rgid = ev.event_data.id_.r.rgid
            ret.egid = ev.event_data.id_.e.egid
        elif ev.what == PROC_EVENT_EXIT:
            ret = ExitProcEvent()
            ret.process_pid = ev.event_data.exit_.process_pid
            ret.process_tgid = ev.event_data.exit_.process_tgid
            ret.exit_code = ev.event_data.exit_.exit_code
            ret.exit_signal = ev.event_data.exit_.exit_signal
        else:
            ret = UnknownProcEvent()

        ret.what = ev.what
        ret.cpu = ev.cpu
        ret.timestamp_ns = ev.timestamp_ns

        return ret
